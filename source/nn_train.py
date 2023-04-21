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

from model.NN import NN, DatasetUtil

n_days_lookahead = int(input('Please input the length of days lookahead in {5, 7, 15, 30, 45, 60, 90, 120}: '))

if(n_days_lookahead not in [5, 7, 15, 30, 45, 60, 90, 120]):
    print('Input does not meet requirements.')
    exit()

data_type = str(input('Please specify the coverage of the data {A - Manufacturer 1, B - Manufacturer 2, C - Manufacturer 1 & 2, D - Unbalanced}:  '))

if(data_type not in ['A', 'B', 'C', 'D']):
    print('Input does not meet requirements.')
    exit()

dit_str = {'A': 'mc1', 'B': 'mc2', 'C': 'mc1_mc2', 'D': 'unbalanced'}


def loadData():

    if dit_str[data_type] not in ('unbalanced'):
        X_train = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_train.npy', allow_pickle=True)
        y_train = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/train_labels.npy', allow_pickle=True)
    else:
        X_train = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_train_rf.npy', allow_pickle=True)
        y_train = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/train_labels_rf.npy', allow_pickle=True)
    X_test = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/smart_test.npy', allow_pickle=True)
    y_test = np.load('../data/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/test_labels.npy', allow_pickle=True)
    X_train = X_train.astype('float32')
    y_train = y_train.astype('float32')
    X_test = X_test.astype('float32')
    y_test = y_test.astype('float32')

    state = np.random.get_state()
    np.random.set_state(state)
    np.random.shuffle(X_train)
    np.random.set_state(state)
    np.random.shuffle(y_train)

    return X_train, y_train, X_test, y_test


def print_all_metrics(true, predicted):
    print(metrics.classification_report(true, predicted, digits=5))


print('-------------------- Loading Data -------------------')
X_train, y_train, X_test, y_test = loadData()

print('------------------ NN ------------------')
num_epochs = 1500
batch_size = 512
lr = 0.0002
if(dit_str[data_type] != 'mc1_no_aging_attr'):
    input_size = 330
    hidden_size = 512
else:
    input_size = 90
    hidden_size = 128
output_size = 1
num_layers = 2
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)


model = NN(input_size=input_size, hidden_size=hidden_size, output_size=output_size).to(device)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

X_train = X_train.reshape((len(X_train), -1))
X_test = X_test.reshape((len(X_test), -1))

# print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
train_dataset = DatasetUtil(X_train, y_train)
test_dataset = DatasetUtil(X_test, y_test)
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=True)

#------------------- Train -------------------#
total_step = len(train_loader)
Loss_list = []
Loss_i = 0
for epoch in range(num_epochs):
    print('training', epoch)
    for i, (X, y) in enumerate(train_loader):
        X = X.to(device)
        y = y.to(device)
        outputs = model(X)
        loss = criterion(outputs.squeeze(), y.squeeze())

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        Loss_list.append(loss.item())
        Loss_i += 1

        pass

    if epoch % 50 == 0:
        print('testing', epoch)
        y_predicted = []
        y_true = []
        with torch.no_grad():
            total = 0
            for i, (X, y) in enumerate(test_loader):
                X = X.to(device)
                y = y.to(device)
                predicted = model(X)
                predicted = torch.tensor([1 if x[0] > 0.5 else 0 for x in predicted]).to(device)
                for j in range(0, len(y)):
                    y_predicted.append(predicted[j].cpu())
                    y_true.append(y[j].cpu())

        print_all_metrics(np.asarray(y_true).astype('int'), np.asarray(y_predicted))
    pass

print('final testing')
y_predicted = []
y_true = []
with torch.no_grad():
    total = 0
    for i, (X, y) in enumerate(test_loader):
        X = X.to(device)
        y = y.to(device)
        predicted = model(X)
        predicted = torch.tensor([1 if x[0] > 0.5 else 0 for x in predicted]).to(device)
        for j in range(0, len(y)):
            y_predicted.append(predicted[j].cpu())
            y_true.append(y[j].cpu())

print_all_metrics(np.asarray(y_true).astype('int'), np.asarray(y_predicted))
torch.save(model.state_dict(), '../trained_model/' + dit_str[data_type] + '/' + str(n_days_lookahead) + '_days_lookahead/nn.pth')
print('Done')