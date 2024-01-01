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
            return

        similardata=getAmplitudedata(date,stocks_data)
        if similardata is None:
            return
        table_name = tbs.TABLE_CN_STOCK_AMPLITUDE['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_AMPLITUDE['columns'])

        data = pd.DataFrame(similardata)
        columns = tuple(tbs.TABLE_CN_STOCK_AMPLITUDE['columns'])
        data.columns = columns

        # 单例，时间段循环必须改时间
        date_str = date.strftime("%Y-%m-%d")
        if date.strftime("%Y-%m-%d") != data.iloc[0]['date']:
            data['date'] = date_str
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
        print(f"amplitude_job save to databbase：{date} 策略 {table_name}")

    except Exception as e:
        logging.error(f"amplitude_job.prepare处理异常：{e}")

def getAmplitudedata(date,stocks_data,threshold=600):
    allstocks = stocks_data.copy()
    todaystr = date.strftime("%Y-%m-%d")

    alllimitupdata=[]
    for keys,values in allstocks.items():
        mask = (values['date'] <= todaystr)
        headstock_value = values.loc[mask].copy()
        allCount=len(headstock_value)
        headstock_value=headstock_value.tail(n=threshold)
        headstock_value.reset_index(inplace=True, drop=True)

        headstock_key = list(keys)
        headstock_key[0] = todaystr

        amplitude_today=max(abs(headstock_value.iloc[-1]['quote_change']),abs(headstock_value.iloc[-1]['amplitude']))

        p_change = headstock_value.iloc[-1]['p_change']
        if p_change<0:
            amplitude_today=-amplitude_today

        headstock_key.append(amplitude_today)
        headstock_key.append(headstock_value.iloc[-1]['amount']/100000000)
        headstock_key.append(allCount)

        headstock_key.append(GetDayAmplitude(headstock_value,5))
        headstock_key.append(GetDayAmplitude(headstock_value,10))
        headstock_key.append(GetDayAmplitude(headstock_value,20))
        headstock_key.append(GetDayAmplitude(headstock_value,40))
        headstock_key.append(GetDayAmplitude(headstock_value,80))
        #mask = (abs(headstock_value['quote_change']) > 5)
        #amplitude5 = headstock_value.loc[mask].copy()
        headstock_key.append(GetDayAmplitude(headstock_value,len(headstock_value)))

        alllimitupdata.append(headstock_key)

    return alllimitupdata


def GetDayAmplitude(data,day):
    amplitudemax = 4
    data1=data.tail(n=day)
    amplitude5 = data1[(abs(data1['quote_change']) > amplitudemax) | (abs(data1['amplitude']) > amplitudemax)]
    return len(amplitude5)

def main():
    runt.run_with_args(prepare)

    # main函数入口
if __name__ == '__main__':
    main()