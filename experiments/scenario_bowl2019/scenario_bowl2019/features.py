import os
from glob import glob

import numpy as np
import pandas as pd
from collections import Counter

from scenario_bowl2019.const import DATASET_FILE, COL_ID


def _random(conf):
    all_clients = pd.read_csv(os.path.join(conf['data_path'], DATASET_FILE)).set_index(COL_ID)
    all_clients = all_clients.assign(random=np.random.rand(len(all_clients)))
    return all_clients[['random']]


def _handcrafted_features(conf):
    df_train = pd.read_pickle(os.path.join(conf['data_path'], 'train.p'))
    df_test = pd.read_pickle(os.path.join(conf['data_path'], 'test.p'))
    df_dataset = df_train + df_test

    df_features = pd.DataFrame([
        {
            COL_ID : x[COL_ID],
            'game_sessions': x['feature_arrays']['game_session'].max(),
            **{'event_id_' + str(k):v for k,v in Counter(x['feature_arrays']['event_id']).items()},
            **{'event_code_' + str(k):v for k,v in Counter(x['feature_arrays']['event_code']).items()},
            **{'event_type_' + str(k):v for k,v in Counter(x['feature_arrays']['event_type']).items()},
            **{'title_' + str(k):v for k,v in Counter(x['feature_arrays']['title']).items()},
            **{'world_' + str(k):v for k,v in Counter(x['feature_arrays']['world']).items()},
            # **{'correct_' + str(k):v for k,v in Counter(x['feature_arrays']['correct']).items()},
        } for x in df_dataset]
    ).set_index(COL_ID).fillna(0)

    return df_features


def _small_group_stat(conf):
    transactions_train = pd.read_csv(os.path.join(conf['data_path'], 'transactions_train.csv'))
    transactions_test = pd.read_csv(os.path.join(conf['data_path'], 'transactions_test.csv'))
    df_transactions = pd.concat([transactions_train, transactions_test])

    cat_counts_train = pd.concat([
        df_transactions.pivot_table(
            index=COL_ID, columns='small_group', values='amount_rur', aggfunc='count').fillna(0.0),
        df_transactions.pivot_table(
            index=COL_ID, columns='small_group', values='amount_rur', aggfunc='mean').fillna(0.0),
        df_transactions.pivot_table(
            index=COL_ID, columns='small_group', values='amount_rur', aggfunc='std').fillna(0.0),
    ], axis=1, keys=['small_group_count', 'small_group_mean', 'small_group_std'])

    cat_counts_train.columns = ['_'.join(map(str, c)) for c in cat_counts_train.columns.values]
    return cat_counts_train


def _metric_learning_embeddings(conf, file_name):
    df = pd.read_pickle(os.path.join(conf['data_path'], file_name)).set_index(COL_ID)
    return df


def load_features(
        conf,
        use_random=False,
        use_handcrafted_features=False,
        metric_learning_embedding_name=None,
        target_scores_name=None,
):
    features = []
    if use_random:
        features.append(_random(conf))

    if use_handcrafted_features:
        features.append(_handcrafted_features(conf))

    if metric_learning_embedding_name is not None:
        features.append(_metric_learning_embeddings(conf, metric_learning_embedding_name))

    return features

def load_scores(conf, target_scores_name):
    valid_files = glob(os.path.join(conf['data_path'], target_scores_name, 'valid', '*'))
    valid_scores = [pd.read_pickle(f).set_index(COL_ID) for f in valid_files]

    test_files = glob(os.path.join(conf['data_path'], target_scores_name, 'test', '*'))
    test_scores = [pd.read_pickle(f).set_index(COL_ID) for f in test_files]

    return valid_scores, test_scores