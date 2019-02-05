import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from numba import jit
import numpy as np
from datetime import timezone
import calendar
from datetime import timedelta

from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
import time

@jit
def np_vwap():
    return np.cumsum(df_trades['p']*(df_trades['p'])) / np.cumsum(df_trades['p'])




#Gets local time in given format
def get_current_local_time(date_input):
        TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        local = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
        print ("Local:", local.strftime(TIME_FORMAT))


#Converts UTC time to local time
def utc_2_local(date_input):
        TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        
        date_input = datetime.strptime(date_input, TIME_FORMAT)
        date_input = date_input - timedelta(hours=4)
        date_input = date_input.strftime(TIME_FORMAT)

        return date_input



def get_file(ticker):
    df_trades = pd.read_csv("C:\\Users\\Admin\\Desktop\\Github\\Limit_order\\Intraday_quotes\\trades-" + ticker + ".csv")
    df_trades = df_trades[50:]
    df_trades = df_trades.reset_index(drop=True)  
    df_trades['vwap'] = np_vwap()   
    target = []
    feature2 = []
    for i in range(0,len(df_trades)):
        try:
            tmp = (df_trades['p'][i - 1] + df_trades['p'][i - 2])/2
            difference = np.sign(df_trades['p'][i] - tmp)
            target.append(difference)
            feature2.append(df_trades['p'][i-1] - df_trades['p'][i])  
        except:
            pass
    df_trades = df_trades[2:]
    df_trades = df_trades.reset_index(drop=True)   
    df_trades['target'] = pd.Series(target)
    df_trades['predicator'] = df_trades['vwap'] - df_trades['p']
    df_trades['feature2'] = feature2
        
    predicators = ['predicator','feature2']
    X = df_trades[predicators]
    y = df_trades.target
    y = y.to_frame()


    return X,y







ticker_list = pd.read_csv("tick_data.csv")

#we drop the first 50 ticks in case there is bad data in the first pre-market
#trades:
#['condition1', 'condition2', 'condition3', 'condition4', 'exchange', 'price', 'size', 'timestamp']
df_trades = pd.read_csv("C:\\Users\\Admin\\Desktop\\Github\\Limit_order\\Intraday_quotes\\trades-CBRL.csv")
df_trades = df_trades[50:]
df_trades = df_trades.reset_index(drop=True)   

#quotes
#['askexchange', 'askprice', 'asksize', 'bidexchange', 'bidprice', 'bidsize', 'condition', 'timestamp']
df_quotes = pd.read_csv("C:\\Users\\Admin\\Desktop\\Github\\Limit_order\\Intraday_quotes\\quotes-CBRL.csv")
df_quotes = df_quotes[50:]
df_quotes = df_quotes.reset_index(drop=True)   

df_trades['vwap'] = np_vwap()



target = []
feature2 = []
for i in range(0,len(df_trades)):
    try:
        tmp = (df_trades['p'][i - 1] + df_trades['p'][i - 2])/2
        difference = np.sign(df_trades['p'][i] - tmp)
        target.append(difference)
        feature2.append(df_trades['p'][i-1] - df_trades['p'][i])  
    except:
        print(i)
        pass
df_trades = df_trades[2:]
df_trades = df_trades.reset_index(drop=True)   
df_trades['target'] = pd.Series(target)
df_trades['predicator'] = df_trades['vwap'] - df_trades['p']
df_trades['feature2'] = feature2



a = int(str(df_trades['t'][5])[:-3])
b = int(str(df_trades['t'][len(df_trades)-5])[:-3])


first_tick = datetime.utcfromtimestamp(a).strftime('%Y-%m-%d %H:%M:%S')
last_tick = datetime.utcfromtimestamp(b).strftime('%Y-%m-%d %H:%M:%S')



print('first tick is at %s'%utc_2_local(first_tick))
print('last tick is at %s'%utc_2_local(last_tick))




#######
### exemple tick by tick ::  price / volume

plt.subplot2grid((3,2), (0,0), colspan=2,rowspan=2)  
plt.plot(df_trades['p'])
plt.plot(df_trades['vwap'])
plt.ylabel('price and vwap')
plt.xlabel('tick by tick') 

plt.subplot2grid((3,2), (2,0), colspan=2)
plt.plot(df_trades['s'])
plt.ylabel('volume')
plt.xlabel('tick by tick') 



####machine learning

models = []
#models.append(('SVC', svm.SVC()))
#models.append(('LR', LogisticRegression()))
#models.append(('CART', DecisionTreeClassifier()))
#models.append(('LDA', LinearDiscriminantAnalysis()))
#models.append(('KNN', KNeighborsClassifier()))
#models.append(('RF',RandomForestClassifier()))
#models.append(('MLP',MLPClassifier()))
#models.append(('GB',GradientBoostingClassifier())) 

models.append(('NB', GaussianNB()))


predicators = ['predicator','feature2']
X = df_trades[predicators]
y = df_trades.target
y = y.to_frame()








ticker_list = pd.read_csv("tick_data.csv")

different_stock = []
testtest= []
for k in range(0,3):
    
    results = []
    
    X,y = get_file(ticker_list['Ticker'][k])
    
    
    test = []
    i = 1
    for j in range(0,len(models)):
        start = time.time()
        cpt = 0
        try:
            while(i < len(df_trades)):
                cpt = cpt + (df_trades['t'][i] - df_trades['t'][i-1])
                if (cpt > 50): #we forecast if and only if we have the 50ms interval threashold
                    model = models[j][1].fit(X[i:i+20],y[i:i+20])
                    prediction = model.predict(X[i+20:i+21])
                    results.append(model.score(X[i+20:i+21], y[i+20:i+21]))
                    cpt = 0 #we reset the interval

                i = i + 1
        except:
            pass
        test.append(results)
        a = sum(results)/len(results)
        duration = time.time() - start
        print('{0}s'.format(duration))
        print('the accuracy of our prediction is in average %s percent'%a)
    different_stock.append(a)
    testtest.append(results)
    
    
    
list_toadd = []
list_toadd_cut = []
for i in range(0,len(df_trades)):
    try:
        if(df_trades['t'][i] - df_trades['t'][i-1] < 1000 and df_trades['t'][i] - df_trades['t'][i-1] > 10): #we want to know if besides block order we need to use c++
            list_toadd_cut.append(df_trades['t'][i] - df_trades['t'][i-1])
    except: 
        print('lol %s'%i)





#mean_ms = sum(list_toadd) /len(list_toadd)


new_cut = []
for i in range(0,len(list_toadd_cut)):
    new_cut.append([list_toadd_cut[i],list_toadd_cut.count(list_toadd_cut[i])])
new_cut.sort(key=lambda x: x[0])
X_r = [ x[0] for x in new_cut]
Y_r = [ x[1] for x in new_cut]

plt.plot(X_r,Y_r)
plt.ylabel('number of ms between two ticks')
plt.xlabel('occurence') 


    



###### ---- why we need c++ 

models = []
models.append(('NB', GaussianNB()))

ticker_list = pd.read_csv("tick_data.csv")
X,y = get_file(ticker_list['Ticker'][0])
i = 500

start = time.time()
model = models[j][1].fit(X[i:i+20],y[i:i+20])
prediction = model.predict(X[i+20:i+21])
if (prediction == 1):
    bid_tosend = df_quotes['bP'][i+20:i+21]
else: 
    bid_tosend = df_quotes['aP'][i+20:i+21]

duration = time.time() - start
print('{0}s'.format(duration))
    