from sklearn.tree import DecisionTreeClassifier as DTC
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.preprocessing import normalize
from sklearn import metrics

import numpy as np
from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
import joblib

from utils import model_and_dataset_selection

n_days_lookahead, data_type, data_folder_name_dict, model_type, model_folder_name_dict = model_and_dataset_selection.train_select_offline()


n = {5: 20000, 7: 20000, 15: 20000, 30: 20000, 45: 20000, 60: 20000, 90: 20000, 120: 20000}


def loadData():

    if data_type != 'D':
        X_train = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_train.npy', allow_pickle=True)
        y_train = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/train_labels.npy', allow_pickle=True)
    else:
        X_train = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_train_rf.npy', allow_pickle=True)
        y_train = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/train_labels_rf.npy', allow_pickle=True)
    X_test = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_test.npy', allow_pickle=True)
    y_test = np.load('../data/' + data_folder_name_dict[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/test_labels.npy', allow_pickle=True)
    X_train = X_train[0:n[n_days_lookahead]].astype('float32')
    y_train = y_train[0:n[n_days_lookahead]].astype('float32')
    X_test = X_test.astype('float32')
    y_test = y_test.astype('float32')

    state = np.random.get_state()
    np.random.set_state(state)
    np.random.shuffle(X_train)
    np.random.set_state(state)
    np.random.shuffle(y_train)

    return X_train, y_train, X_test, y_test


def print_all_metrics(true, predicted):
    print(metrics.classification_report(true, predicted, digits=5), metrics.roc_auc_score(true, predicted))


X_train, y_train, X_test, y_test = loadData()

print('------------------ Loading Data ------------------')
X_train = X_train.reshape((len(X_train), -1))
X_test = X_test.reshape((len(X_test), -1))

print('------------------ Decision Tree ------------------')
if (data_type == 'C'):
    if (n_days_lookahead == 5):
        model_dtc = DTC(criterion='gini', max_depth=30, max_leaf_nodes=100, min_impurity_decrease=0.0, min_samples_leaf=1)
    elif (n_days_lookahead == 7):
        model_dtc = DTC(criterion='gini', max_depth=50, max_leaf_nodes=100, min_impurity_decrease=0.0, min_samples_leaf=3)
    elif (n_days_lookahead == 15):
        model_dtc = DTC(criterion='gini', max_depth=80, max_leaf_nodes=100, min_impurity_decrease=0.0, min_samples_leaf=1)
    elif (n_days_lookahead == 30):
        model_dtc = DTC(criterion='gini', max_depth=10, max_leaf_nodes=None, min_impurity_decrease=0.0, min_samples_leaf=2)
    elif (n_days_lookahead == 45):
        model_dtc = DTC(criterion='entropy', max_depth=30, max_leaf_nodes=100, min_impurity_decrease=0.0, min_samples_leaf=2)
    elif (n_days_lookahead == 60):
        model_dtc = DTC(criterion='gini', max_depth=30, max_leaf_nodes=100, min_impurity_decrease=0.0, min_samples_leaf=2)
    elif (n_days_lookahead == 90):
        model_dtc = DTC(criterion='gini', max_depth=30, max_leaf_nodes=None, min_impurity_decrease=0.0, min_samples_leaf=1)
    elif (n_days_lookahead == 120):
        model_dtc = DTC(criterion='entropy', max_depth=30, max_leaf_nodes=None, min_impurity_decrease=0.0, min_samples_leaf=1)
else:
    model_dtc = DTC()
model_dtc.fit(X_train, y_train)
y_pred = model_dtc.predict(X_test)
print_all_metrics(y_test, y_pred)
joblib.dump(model_dtc, '../trained_model/' + model_folder_name_dict[model_type] + '/' + str(n_days_lookahead) + '_days_lookahead/dt.pkl')
print('Done')
