#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import logging
import concurrent.futures
import pandas as pd
import os.path
import numpy as np
import sys
import instock.core.crawling.stock_hist_em as she
import instock.core.kline.klineSimilar_corrcoef as corrcoef
import datetime
import json

#from datetime import datetime, timedelta

import time

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
logging.getLogger().setLevel(logging.INFO)

import instock.lib.run_template as runt
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.core.indicator.calculate_indicator as idr
import instock.core.kline.klineSimilar_corrcoef as ksc
from instock.core.singleton_stock import stock_hist_data
import instock.lib.trade_time as trd
from tqdm import tqdm

__author__ = 'myh '
__date__ = '2023/3/10 '

laststocks_data=[]

def prepare(date):
    try:
        stocks_data = stock_hist_data(date=date).get_data()
        if stocks_data is None:
            return None

        allstockdatas={}

        maxdatalength=0
        threshold = 360
        for keys,values in stocks_data.items():
            end_date = date.strftime("%Y-%m-%d")
            mask = (values['date'] <= end_date)
            values = values.loc[mask]

            if len(values) >= threshold:
                values = values.tail(n=threshold)
                values.reset_index(inplace=True, drop=True)

            maxdata=  values['close'].values.max()
            mindata = values['close'].values.min()
            #allrange=maxdata-mindata
            values['close']=values['close'].values/maxdata*100
            allstockdatas[keys]= values['close'].to_list()
            if len(values)>maxdatalength:
                maxdatalength=len(values)


        allstockdatasjson = {}
        for keys,values in allstockdatas.items():
            json_key=json.dumps(keys,ensure_ascii=False)
            if len(values)<maxdatalength:
                for addindex in range(0,maxdatalength-len(values)):
                    values.insert(0,0)

            json_data=json.dumps(values,ensure_ascii=False)

            allstockdatasjson[keys[2]]=values


        return allstockdatasjson
    except Exception as e:
        logging.error(f"kline_limitup_job.prepare处理异常：{e}")

def main():
    run_date, run_date_nph = trd.get_trade_date_last()
    return prepare(run_date)

    # main函数入口
if __name__ == '__main__':
    data=main()
    json_data = json.dumps(data,ensure_ascii=False)
    print(len(data))