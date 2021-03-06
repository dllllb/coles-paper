import os
from glob import glob

import pandas as pd

from scenario_x5.const import COL_ID


def _metric_learning_embeddings(conf, file_name):
    df = pd.read_pickle(os.path.join(conf['data_path'], file_name)).set_index(COL_ID)
    return df


def load_features(
        conf,
        metric_learning_embedding_name=None
):
    features = []

    if metric_learning_embedding_name is not None:
        if type(metric_learning_embedding_name) is not list:
            metric_learning_embedding_name = [metric_learning_embedding_name]
        for f_name in metric_learning_embedding_name:
            features.append(_metric_learning_embeddings(conf, f_name))

    if len(features) > 1:
        for i, df in enumerate(features):
            df.columns = [f'{col}__{i}' for col in df.columns]
    return features


def load_scores(conf, target_scores_name):
    valid_files = glob(os.path.join(conf['data_path'], target_scores_name, 'valid', '*'))
    valid_scores = [pd.read_pickle(f).set_index(COL_ID) for f in valid_files]

    test_files = glob(os.path.join(conf['data_path'], target_scores_name, 'test', '*'))
    test_scores = [pd.read_pickle(f).set_index(COL_ID) for f in test_files]

    return valid_scores, test_scores
