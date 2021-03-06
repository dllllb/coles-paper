import torch
import numpy as np
from math import sqrt

from functools import partial
from ignite.metrics import EpochMetric, Metric
import ignite.metrics
from scipy.special import softmax


def outer_pairwise_distance(A, B=None):
    """
        Compute pairwise_distance of Tensors
            A (size(A) = n x d, where n - rows count, d - vector size) and
            B (size(A) = m x d, where m - rows count, d - vector size)
        return matrix C (size n x m), such as C_ij = distance(i-th row matrix A, j-th row matrix B)

        if only one Tensor was given, computer pairwise distance to itself (B = A)
    """

    if B is None: B = A

    max_size = 2 ** 26
    n = A.size(0)
    m = B.size(0)
    d = A.size(1)

    if n * m * d <= max_size or m == 1:

        return torch.pairwise_distance(
            A[:, None].expand(n, m, d).reshape((-1, d)),
            B.expand(n, m, d).reshape((-1, d))
        ).reshape((n, m))

    else:

        batch_size = max(1, max_size // (n * d))
        batch_results = []
        for i in range((m - 1) // batch_size + 1):
            id_left = i * batch_size
            id_rigth = min((i + 1) * batch_size, m)
            batch_results.append(outer_pairwise_distance(A, B[id_left:id_rigth]))

        return torch.cat(batch_results, dim=1)


def outer_cosine_similarity(A, B=None):
    """
        Compute cosine_similarity of Tensors
            A (size(A) = n x d, where n - rows count, d - vector size) and
            B (size(A) = m x d, where m - rows count, d - vector size)
        return matrix C (size n x m), such as C_ij = cosine_similarity(i-th row matrix A, j-th row matrix B)

        if only one Tensor was given, computer pairwise distance to itself (B = A)
    """

    if B is None: B = A

    max_size = 2 ** 32
    n = A.size(0)
    m = B.size(0)
    d = A.size(1)

    if n * m * d <= max_size or m == 1:

        A_norm = torch.div(A.transpose(0, 1), A.norm(dim=1)).transpose(0, 1)
        B_norm = torch.div(B.transpose(0, 1), B.norm(dim=1)).transpose(0, 1)
        return torch.mm(A_norm, B_norm.transpose(0, 1))

    else:

        batch_size = max(1, max_size // (n * d))
        batch_results = []
        for i in range((m - 1) // batch_size + 1):
            id_left = i * batch_size
            id_rigth = min((i + 1) * batch_size, m)
            batch_results.append(outer_cosine_similarity(A, B[id_left:id_rigth]))

        return torch.cat(batch_results, dim=1)


def metric_Recall_top_K(X, y, K, metric='cosine'):
    """
        calculate metric R@K
        X - tensor with size n x d, where n - number of examples, d - size of embedding vectors
        y - true labels
        N - count of closest examples, which we consider for recall calcualtion
        metric: 'cosine' / 'euclidean'.
            !!! 'euclidean' - to slow for datasets bigger than 100K rows
    """
    res = []

    n = X.size(0)
    d = X.size(1)
    max_size = 2 ** 32
    batch_size = max(1, max_size // (n*d))

    with torch.no_grad():

        for i in range(1 + (len(X) - 1) // batch_size):

            id_left = i*batch_size
            id_right = min((i+1)*batch_size, len(y))
            y_batch = y[id_left:id_right]

            if metric == 'cosine':
                pdist = -1 * outer_cosine_similarity(X, X[id_left:id_right])
            elif metric == 'euclidean':
                pdist = outer_pairwise_distance(X, X[id_left:id_right])
            else:
                raise AttributeError(f'wrong metric "{metric}"')

            values, indices = pdist.topk(K + 1, 0, largest=False)

            y_rep = y_batch.repeat(K, 1)
            res.append((y[indices[1:]] == y_rep).sum().item())

    return np.sum(res) / len(y) / K


class ignite_Recall_top_K(EpochMetric):

    def __init__(self, output_transform=lambda x: x, K=3, metric='cosine'):
        super(ignite_Recall_top_K, self).__init__(
            partial(metric_Recall_top_K, K=K, metric=metric),
            output_transform=output_transform
        )


class BatchRecallTop(Metric):
    def __init__(self, k, metric='cosine'):
        super().__init__(output_transform=lambda x: x)

        self.num_value = 0.0
        self.denum_value = 0

        self.k = k
        self.metric = metric

    def reset(self):
        self.num_value = 0.0
        self.denum_value = 0

        super().reset()

    def update(self, output):
        x, y = output
        value = metric_Recall_top_K(x, y, self.k, self.metric)

        self.num_value += value
        self.denum_value += 1

    def compute(self):
        if self.denum_value == 0:
            return 0.0
        return self.num_value / self.denum_value


#custom class
from ignite.metrics.metric import sync_all_reduce, reinit__is_reduced
class SpendPredictMetric(ignite.metrics.Metric):
  def __init__(self, ignored_class=None, output_transform=lambda x: x):
      self._relative_error = None
      super(SpendPredictMetric, self).__init__(output_transform=output_transform)

  @reinit__is_reduced
  def reset(self):
      self._relative_error = []
      super(SpendPredictMetric, self).reset()

  @reinit__is_reduced
  def update(self, output):
      y_pred, y = output
      delta = torch.abs(y_pred[:,0] - y[:,0])
      rel_delta = 100*delta / torch.max(y[:,0], torch.exp(y[:,0]-y[:,0]) )
      self._relative_error += [torch.mean(rel_delta).item()]

  @sync_all_reduce("_relative_error")
  def compute(self):
     if self._relative_error == 0:
       raise NotComputableError('CustomAccuracy must have at least one example before it can be computed.')
     return sum(self._relative_error)/len(self._relative_error)

#cosine similarity between prediction and ground truth
#from 0 to 1, the lower is better
#sum(y_pred)=1 sum(y)=1
#sum(y_pred)=1 sum(y)=1
from ignite.metrics.metric import sync_all_reduce, reinit__is_reduced
class PercentPredictMetric(ignite.metrics.Metric):
   def __init__(self, ignored_class=None, output_transform=lambda x: x):
       self._relative_error = None
       self.softmax = torch.nn.Softmax(dim=1)
       super(PercentPredictMetric, self).__init__(output_transform=output_transform)

   @reinit__is_reduced
   def reset(self):
       self._relative_error = []
       super(PercentPredictMetric, self).reset()
   @reinit__is_reduced

   def update(self, output):
       y_pred, y = output
       soft_pred = self.softmax(y_pred[:,1:53])
       delta=torch.nn.functional.cosine_similarity(soft_pred, y[:,1:53], dim=1)
       rel_delta = -torch.mean(delta)+1 #from 0 to 1, low is better
       self._relative_error += [rel_delta.item()]

   @sync_all_reduce("_relative_error")
   def compute(self):
       if self._relative_error == 0:
          raise NotComputableError('CustomAccuracy must have at least one example before it can be computed.')
       return sum(self._relative_error)/len(self._relative_error)                                                                                                                             
#r2 metric
#sum(y_pred)=1 sum(y)=1 
#if metric > 0 it means, that the prediction is better than mean value, max value 1
from ignite.metrics.metric import sync_all_reduce, reinit__is_reduced
class PercentR2Metric(ignite.metrics.Metric):

    def __init__(self, ignored_class=None, output_transform=lambda x: x):
       self._relative_error = None
       self.softmax = torch.nn.Softmax(dim=1)
       super(PercentR2Metric, self).__init__(output_transform=output_transform)

    @reinit__is_reduced
    def reset(self):
        self._relative_error = []
        super(PercentR2Metric, self).reset()

    @reinit__is_reduced
    def update(self, output):
         y_pred, y = output
         soft_pred = self.softmax(y_pred[:,1:53])
         rss = torch.norm(soft_pred - y[:,1:53], p=1, dim=1)**2
         apriori_mean = y[:,1:53].mean(dim=0)
         apriori_mean = apriori_mean.repeat(y_pred.shape[0], 1)
         tss = torch.norm(soft_pred - apriori_mean, p=1, dim=1)**2
         r2 = 1 - rss/tss
         self._relative_error += [r2.mean().item()]
 
    @sync_all_reduce("_relative_error")
    def compute(self):
         if self._relative_error == 0:
            raise NotComputableError('CustomAccuracy must have at least one example before it can be computed.')
         return sum(self._relative_error)/len(self._relative_error)


