import json
from urllib.request import urlopen
import urllib
from datetime import datetime
from datetime import timedelta
import csv
import os
import time
import pandas as pd
from process_data_csv import nextDay


folder_path = "C:\\Users\\Admin\\Desktop\\Week_2\\Intraday_quotes\\"

def url_trades(ticker,date):
    KEY = "CN3VkwU_c4C5_Q4_PXiLtsiio_YXMT0EFxiWZK"
    supplement = "?limit=10000&apiKey="
    url = "https://api.polygon.io/v1/historic/" + "trades/" + ticker + "/" + date + supplement + KEY
    return url
    
def url_quotes(ticker,date):
    KEY = "CN3VkwU_c4C5_Q4_PXiLtsiio_YXMT0EFxiWZK"
    supplement = "?limit=10000&apiKey="
    url = "https://api.polygon.io/v1/historic/" + "quotes/" + ticker + "/" + date + supplement + KEY
    return url



def get_json_data(ticker,date):
    """Request data as json from finance.yahoo.com

    :param ticker:
    :param expiration_date: optional
    :param return_value: optional
    :return: json object as required by return_value
    """
    url_1 = url_trades(ticker,date)
    url_2 = url_quotes(ticker,date)

    try:
        chain_json1 = json.load(urlopen(url_1))
        chain_json2 = json.load(urlopen(url_2))
        
    except urllib.URLError as e:
        if hasattr(e, 'reason'):
            print ('We failed to reach a server.')
            print ('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print ('The server couldn\'t fulfill the request.')
            print ('Error code: ', e.code)
        print ('Unable to retrieve required data.')
        print ('Possible reasons:\n1. No Internet connection - check and/or try again later.')
        print ('2. No such ticker {0}\n3. There are no options for ticker {0}'.format(ticker))
        return []

    return chain_json1,chain_json2



def main(ticker,folder_path,date):
    
    
    file_name1 = folder_path + '\\' + "trades" + "-" + '{}.csv'.format(ticker)
    file_name2 = folder_path + '\\' + "quotes" + "-" + '{}.csv'.format(ticker)
 
    
    trades_data,quotes_data = get_json_data(ticker,date)
    
    
    
    delete_index_list =[]
    for i in range(0,len(trades_data)):
        if(len(trades_data['ticks'][i]) != 8):
            delete_index_list.append(i)
            
    for i in range(0,len(quotes_data)):
        if(len(quotes_data['ticks'][i]) != 8):
            delete_index_list.append(i)
            
    delete_index_list = list(set(delete_index_list))

    for i in sorted(delete_index_list, reverse=True):
        del trades_data['ticks'][i]
        del quotes_data['ticks'][i]
    
    
    try:
        #['condition1', 'condition2', 'condition3', 'condition4', 'exchange', 'price', 'size', 'timestamp']
        keys = trades_data['ticks'][0].keys()
        with open(file_name1 , 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(trades_data['ticks'])
    
        #['askexchange', 'askprice', 'asksize', 'bidexchange', 'bidprice', 'bidsize', 'condition', 'timestamp']
        keys = quotes_data['ticks'][0].keys()
        with open(file_name2, 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(quotes_data['ticks'])
    
        print('we just saved the data for ticker %s'%ticker)
    except:
        print('error, this sucks')
            
    return folder_path     #return the path we need to locate the option csv
                            #otherwise just create the option chain in the file we asked him

    
    

to_backtest = pd.read_csv("backtest.csv")

list_to_store = []
for i in range(1,202):
    ticker = to_backtest['Ticker'][len(to_backtest)-i]
    Day = to_backtest['Day'][len(to_backtest)-i]
    Day = nextDay(Day)

    main(ticker,"C:\\Users\\Admin\\Desktop\\Week_2\\Intraday_quotes\\",Day)
    list_to_store.append([ticker,Day])


    
for j in range(0,len(list_to_store)):    
    with open("C:\\Users\\Admin\\Desktop\\Week_2\\Intraday_quotes\\tick_data.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow(list_to_store[j])


