# -*- coding: utf-8 -*-
"""..FINAL LSTM

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QjUoa0rRDtfb7TMXU9Q6Q-tYgpZy6YMg
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Flatten
import matplotlib.pyplot as plt
# %matplotlib inline
dataset=pd.read_csv("1 year.csv",parse_dates=["date"],dayfirst=True)
dataset.info
dataset.shape

from datetime import datetime,date,time
dataset.dropna()

for i in range(0,dataset['time'].size):
    dataset.loc[i,'time']=datetime.strptime(dataset.loc[i,'time'], '%H:%M').time()

for i in range (0,dataset['time'].size) :
    dataset.loc[i,'days']=pd.Timestamp.combine((dataset.loc[i,'date']),(dataset.loc[i,'time']))

dataset

dataset.dropna(inplace=True)

dataset=dataset.set_index('days')
dataset=dataset.drop(['time'],axis=1)
dataset=dataset.resample('1H').mean()

dataset

dataset.plot()

from statsmodels.tsa.stattools import adfuller
test_result=adfuller(dataset['mcp'])
#Ho: It is non stationary
#H1: It is stationary

def adfuller_test(mcp):
    result=adfuller(mcp)
    labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations Used']
    for value,label in zip(result,labels):
        print(label+' : '+str(value) )
    if result[1] <= 0.05:
        print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data has no unit root and is stationary")
    else:
        print("weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary ")

adfuller_test(dataset['mcp'])

from pandas.plotting import autocorrelation_plot
autocorrelation_plot(dataset['mcp'])
plt.show()

from google.colab import files
dataset.to_csv('updated_dataset.csv', index=False)
files.download('updated_dataset.csv')

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Flatten

# load dataset
dataset = np.genfromtxt('updated_dataset.csv', delimiter=',', skip_header=1, filling_values=np.nan)
n_features = 6
dataset

# print the shape and contents of dataset
print('dataset shape:', dataset.shape)
print('dataset contents:', dataset)

# remove rows with NaN values
dataset = dataset[~np.isnan(dataset).any(axis=1)]
dataset

# split into train and test sets
train_size = int(len(dataset) * 0.67)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
test
train

# scale the data
scaler = MinMaxScaler(feature_range=(0, 1))
train = scaler.fit_transform(train)
test = scaler.transform(test)

look_back = 12

# prepare the training data
trainX, trainY = [], []
for i in range(look_back, len(train)):
    trainX.append(train[i-look_back:i, :n_features])
    trainY.append(train[i, n_features - 1])
trainX, trainY = np.array(trainX), np.array(trainY)

# prepare the testing data
testX, testY = [], []
for i in range(look_back, len(test)):
    testX.append(test[i-look_back:i, :n_features])
    testY.append(test[i, n_features - 1])
testX, testY = np.array(testX), np.array(testY)

# build the LSTM model
model = Sequential()
model.add(LSTM(100, input_shape=(look_back, n_features)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# train the model
history = model.fit(trainX, trainY, epochs=10, batch_size=32, validation_data=(testX, testY), verbose=2)

# make predictions
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)

# calculate the root mean squared error
trainScore = np.sqrt(np.mean(np.square(trainY[0] - trainPredict[:,0])))
print('Train RMSE: %.2f' % (trainScore))
testScore = np.sqrt(np.mean(np.square(testY[0] - testPredict[:,0])))
print('Test RMSE: %.2f' % (testScore))

import matplotlib.pyplot as plt

# plot training and validation loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper right')
plt.show()

import matplotlib.pyplot as plt
plt.figure(figsize=(14, 7))
plt.plot(testY, label='Test Values')
plt.plot(testPredict, label='Predicted Values')
plt.legend()
plt.xticks(range(0, len(testY), 500))  
plt.show()

print('dataset shape:', dataset.shape)
print('train shape:', train.shape)

# Get the last 'look_back' days of data from the dataset
input_data = dataset[-look_back:, :n_features]

# Scale the input data
input_data_scaled = scaler.transform(input_data)

# Reshape the input data to match the model's input shape
input_data_reshaped = np.reshape(input_data_scaled, (1, look_back, n_features))

# Predict the (n+1)th day price
predicted_price_scaled = model.predict(input_data_reshaped)

# Inverse transform the predicted price
predicted_price = scaler.inverse_transform([[0] * (n_features - 1) + [predicted_price_scaled[0, 0]]])

# Print the predicted price for the (n+1)th day
print('Predicted price for (n+1)th day:', predicted_price[0][-1])