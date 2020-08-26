import keras
from keras import layers
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


df = pd.read_csv("./dataset_info.csv", encoding = "UTF-8")
x = df.iloc[:, :-1]
y = df.iloc[:, -1]
len_columns = len(x.columns)
len_x = len(x)
trainlimit = int(len_x * 0.8)
x_train = x[:trainlimit]
x_test = x[trainlimit:]
x_validation = x[trainlimit:int(len_x * 0.9)]
y_train = y[:trainlimit]
y_test = y[trainlimit:]
y_validation = y[trainlimit:int(len_x * 0.9)]
x_mean = x_train.mean(axis = 0)
x_std = x_train.std(axis = 0)
x_train -= x_mean
x_train /= x_std
x_test -= x_mean
x_test /= x_std

'''
# kNN
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
for i in range(60, 100):
    reg = KNeighborsRegressor(i)
    reg.fit(x_train, y_train)
    yp = reg.predict(x_test)
    print("%d %f" % (i, mean_squared_error(y_test, yp)))
'''

class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch':[], 'epoch':[]}
        self.accuracy = {'batch':[], 'epoch':[]}
        self.val_loss = {'batch':[], 'epoch':[]}
        self.val_acc = {'batch':[], 'epoch':[]}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('accuracy'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_accuracy'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('accuracy'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_accuracy'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # acc
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        # loss
        # plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_acc
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            # val_loss
            # plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('acc-loss')
        plt.legend(loc="upper right")
        plt.show()

# nn
# from keras.optimizers import SGD
history = LossHistory()
# train
model = keras.Sequential()
model.add(layers.Dense(units=512, input_dim=len_columns, activation = "hard_sigmoid", bias_initializer=keras.initializers.glorot_normal()))
model.add(layers.Dropout(0.1))
model.add(layers.Dense(units=512, activation = "tanh", bias_initializer=keras.initializers.glorot_normal()))
model.add(layers.Dropout(0.1))
model.add(layers.Dense(units=1024, activation = "relu", bias_initializer=keras.initializers.glorot_normal()))
model.add(layers.Dropout(0.1))
model.add(layers.Dense(units=1))
model.compile(optimizer='adam', loss = 'mae', metrics=["accuracy"])
model.fit(x_train, y_train, 512, 200, callbacks = [history], validation_data = (x_validation, y_validation))
model.summary()
model.save("wow.hdf5")
# evaluate
score = model.evaluate(x_test, y_test)
print(score)
history.loss_plot('epoch')