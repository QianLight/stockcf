#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import logging
import concurrent.futures
import pandas as pd
import os.path
import numpy as np
import sys
import instock.core.crawling.stock_hist_em as she
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

        similardata=getKlinedata(date,stocks_data)
        if similardata is None:
            return
        table_name = tbs.TABLE_CN_STOCK_KLINE_SIMILAR['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_KLINE_SIMILAR['columns'])

        data = pd.DataFrame(similardata)
        columns = tuple(tbs.TABLE_CN_STOCK_KLINE_SIMILAR['columns'])
        data.columns = columns

        # 单例，时间段循环必须改时间
        date_str = date.strftime("%Y-%m-%d")
        if date.strftime("%Y-%m-%d") != data.iloc[0]['date']:
            data['date'] = date_str
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
        print(f"klineSimilar_corrcoef_job save to databbase：{date} 策略 {table_name}")

    except Exception as e:
        logging.error(f"klineSimilar_corrcoef_job.prepare处理异常：{e}")

def getKlinedata(date,stocks_data,threshold=60):
    allstocks = stocks_data.copy()

    similar_others = []
    similar_no_others = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        leavecount = len(allstocks)
        lastexecutor = None
        headstock_key = None
        des_tqdm = " 形态分类:"
        if date is not None:
            des_tqdm = date.strftime("%Y-%m-%d") + des_tqdm
        p = tqdm(total=leavecount, desc=des_tqdm)

        maxvalue = 5
        minvalue = -100
        pchangevalue = 0.1

        while leavecount > 1:
            if lastexecutor is None:
                headstock_key = list(allstocks.keys())[0]
                headstock_value = list(allstocks.values())[0]
                allstocks.pop(headstock_key)
                if len(headstock_value) > 0:
                    pchangevalue = headstock_value.iloc[-1]['p_change']
                else:
                    print(f"klineSimilar_corrcoef_job.len 0：{date} {len(headstock_key)}")

                if len(headstock_value) >= threshold and (pchangevalue >= maxvalue or pchangevalue <= minvalue):
                    headstock_value = headstock_value.tail(n=threshold)
                    lastexecutor = executor.submit(run_check_klinesimilar, headstock_key, headstock_value, allstocks, date)
                else:
                    p.update(leavecount - len(allstocks))
                    leavecount = len(allstocks)

            if lastexecutor is not None:
                if lastexecutor.done():
                    _data_ = lastexecutor.result()
                    headstock_key=list(headstock_key)
                    headstock_key.append(threshold)
                    if _data_ is not None:
                        #similardic[headstock_key] = _data_
                        headstock_key.append(len(_data_))
                        similar_others.append(headstock_key)
                        [allstocks.pop(k) for k in _data_]
                    else:
                        headstock_key.append(0)
                        similar_no_others.append(headstock_key)

                    p.update(leavecount - len(allstocks))
                    leavecount = len(allstocks)

                    lastexecutor = None
            time.sleep(0.01)

    p.close()
    if similar_others is None:
        return None

    print(f"klineSimilar_corrcoef_job.run_check：{date} {len(similar_others)} {len(similar_no_others)}")
    allsimilar=similar_others+(similar_no_others)
    return allsimilar
def run_check_klinesimilar(headstock_key,compareStocks,stocks, date, workers=40):
    data =[]
    nAllCounts=len(stocks)
    nBackIndex=0;

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_data = {executor.submit(ksc.get_klineSimilar,headstock_key,compareStocks, k, stocks[k], date=date): k for k in stocks}
            for future in concurrent.futures.as_completed(future_to_data):
                stock = future_to_data[future]
                try:
                    _data_ = future.result()
                    nBackIndex+=1
                    if _data_:
                        data.append(stock)
                except Exception as e:
                    logging.error(f"klineSimilar_corrcoef_job.run_check处理异常：{stock[1]}代码{e}")
    except Exception as e:
        logging.error(f"klineSimilar_corrcoef_job.run_check处理异常：{e}")
    if not data:
        return None
    else:
        return data


def getklineComparedata(stocks,date):
    _columns = tuple(tbs.TABLE_CN_STOCK_KLINE_SIMILAR['columns'])
    _selcol = '`,`'.join(_columns)

    table_name = tbs.TABLE_CN_STOCK_KLINE_SIMILAR['name']
    sql = f'''SELECT `{_selcol}` FROM `{table_name}` WHERE `date` <= '{date}' '''

    isreadcsv=True
    if isreadcsv:
       klinedata=pd.read_csv('klinesimilar.csv')
       klinedata['code'] = klinedata['code'].astype(str)
       #klinedata['date'] = pd.to_datetime(klinedata['date'])
    else:
       klinedata = pd.read_sql(sql=sql, con=mdb.engine())

    allklinedatas=[]
    for keys,values in stocks.items():
        code=keys[1]
        mask = (klinedata['code'] == code)
        itmkline = klinedata.loc[mask].copy()
        if len(itmkline)==0:
            continue

        for idx, itmdata in itmkline.iterrows():

            if isreadcsv==False:
               end_date = itmdata["date"].strftime("%Y-%m-%d")
            else:
               end_date = itmdata["date"]

            mask = (values['date'] < end_date)
            fitklinedata = values.loc[mask].copy()
            fitklinedata=fitklinedata.tail(n=itmdata["threshold"])
            fitklinedata.insert(1,"name",keys[2])
            fitklinedata.insert(2, "dynamic_para", itmdata["dynamic_para"])
            allklinedatas.append(fitklinedata)

    return allklinedatas

def MA(S,N):              #求序列的N日简单移动平均值，返回序列
    return pd.Series(S).rolling(N).mean().values

def main():
    runt.run_with_args(prepare)

    # main函数入口
if __name__ == '__main__':
    main()