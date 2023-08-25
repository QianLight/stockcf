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

        similardata=getVolumedata(date,stocks_data)
        if similardata is None:
            return
        table_name = tbs.TABLE_CN_STOCK_VOLUME['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_VOLUME['columns'])

        data = pd.DataFrame(similardata)
        columns = tuple(tbs.TABLE_CN_STOCK_VOLUME['columns'])
        data.columns = columns

        # 单例，时间段循环必须改时间
        date_str = date.strftime("%Y-%m-%d")
        if date.strftime("%Y-%m-%d") != data.iloc[0]['date']:
            data['date'] = date_str
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
        print(f"volume_job save to databbase：{date} 策略 {table_name}")

    except Exception as e:
        logging.error(f"volume_job.prepare处理异常：{e}")

def getVolumedata(date,stocks_data,threshold=180):
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

        volume_today=headstock_value.iloc[-1]['volume']
        ratio_last=volume_today/headstock_value.iloc[-2]['volume']

        p_change = headstock_value.iloc[-1]['p_change']
        if p_change<0:
            ratio_last=-ratio_last

        headstock_key.append(ratio_last)

        headstock_key.append(headstock_value.iloc[-1]['amount'])
        headstock_key.append(allCount)

        maxallTime = headstock_value['volume'].values.max()
        daymin_max_ratio = round((volume_today-maxallTime) / volume_today, 2)
        headstock_key.append(daymin_max_ratio)

        max_index = headstock_value['volume'].idxmax() + 1
        daymin_max_ratio_day = len(headstock_value) - max_index
        headstock_key.append(daymin_max_ratio_day)

        minallTime = headstock_value['volume'].values.min()
        daymin_low_ratio = round((volume_today - minallTime) / minallTime, 2)
        headstock_key.append(daymin_low_ratio)

        low_index = headstock_value['volume'].idxmin() + 1
        daymin_low_ratio_day = len(headstock_value) - low_index
        headstock_key.append(daymin_low_ratio_day)

        alllimitupdata.append(headstock_key)

    return alllimitupdata

def main():
    runt.run_with_args(prepare)

    # main函数入口
if __name__ == '__main__':
    main()