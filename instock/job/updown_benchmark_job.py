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
from instock.lib import globaldata

__author__ = 'myh '
__date__ = '2023/3/10 '

laststocks_data=[]

def prepare(date):
    try:
        stocks_data = stock_hist_data(date=date).get_data()
        if stocks_data is None:
            return

        similardata=getdata(date,stocks_data)
        if similardata is None:
            return
        table_name = tbs.TABLE_CN_STOCK_UPDOWN_BENCHMARK['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_UPDOWN_BENCHMARK['columns'])

        data = pd.DataFrame(similardata)
        columns = tuple(tbs.TABLE_CN_STOCK_UPDOWN_BENCHMARK['columns'])
        data.columns = columns

        # 单例，时间段循环必须改时间
        date_str = date.strftime("%Y-%m-%d")
        if date.strftime("%Y-%m-%d") != data.iloc[0]['date']:
            data['date'] = date_str
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
        print(f"updown_benchmark_job save to databbase：{date} 策略 {table_name}")

    except Exception as e:
        logging.error(f"updown_benchmark_job.prepare处理异常：{e}")

def getdata(date,stocks_data,threshold=90):
    allstocks = stocks_data.copy()
    todaystr = date.strftime("%Y-%m-%d")

    benchMarkData=globaldata.GetBenchMark()
    mask = (benchMarkData['date'] <= todaystr)
    benchMarkData = benchMarkData.loc[mask].copy()
    mask = (benchMarkData['ups_downs'] >0)
    benchMarkData_up = benchMarkData.loc[mask].copy()

    mask = (benchMarkData['ups_downs'] <=0)
    benchMarkData_down = benchMarkData.loc[mask].copy()

    alllimitupdata=[]
    for keys,values in allstocks.items():
        mask = (values['date'] <= todaystr)
        headstock_value = values.loc[mask].copy()

        try:
            headstock_value=headstock_value.tail(n=threshold)
            headstock_value.reset_index(inplace=True, drop=True)
            allCount=len(headstock_value)

            headstock_key = list(keys)
            headstock_key[0] = todaystr

            mask = (headstock_value['p_change'] > 0)
            headstock_value_up = headstock_value.loc[mask].copy()
            mask = (headstock_value['p_change'] <= 0)
            headstock_value_down = headstock_value.loc[mask].copy()


            count_up=len(headstock_value_up)
            if count_up>0:
                mask = (headstock_value_up['date'].isin(benchMarkData_up["date"].values))
                headstock_value_up = headstock_value_up.loc[mask].copy()
                ratio_up=(len(headstock_value_up))/count_up

            count_down = len(headstock_value_down)
            if count_down>0:
                mask = (headstock_value_down['date'].isin(benchMarkData_down["date"].values))
                headstock_value_down = headstock_value_down.loc[mask].copy()
                ratio_down=(len(headstock_value_down))/count_down

            ratio=(len(headstock_value_up)+len(headstock_value_down))/allCount
            headstock_key.append(round(ratio,3)*100)
            headstock_key.append(round(ratio_up, 3) * 100)
            headstock_key.append(round(ratio_down, 3) * 100)
        except Exception as e:
            logging.error(f"updown_benchmark_jobgetdata.prepare处理异常：{e}")
        alllimitupdata.append(headstock_key)

    return alllimitupdata


def main():
    runt.run_with_args(prepare)

    # main函数入口
if __name__ == '__main__':
    main()