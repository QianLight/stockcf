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

        allstocks=stocks_data.copy()

        similardic={}
        similardicnone = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            startindex=0;
            leavecount=len(allstocks)
            lastexecutor = None
            headstock_key=None
            threshold=60

            des_tqdm = " 形态分类:"
            if date is not None:
                des_tqdm = date.strftime("%Y-%m-%d") + des_tqdm
            p = tqdm(total=leavecount, desc=des_tqdm)

            maxvalue=1
            minvalue=-100
            pchangevalue=0.1

            while leavecount>1:
                if lastexecutor is None:
                    headstock_key=list(allstocks.keys())[0]
                    headstock_value = list(allstocks.values())[0]
                    allstocks.pop(headstock_key)
                    if len(headstock_value)>0:
                       pchangevalue=headstock_value.iloc[-1]['p_change']
                    else:
                        print(f"klineSimilar_corrcoef_job.len 0：{date} {len(headstock_key)}")

                    if len(headstock_value)>=threshold and (pchangevalue>=maxvalue or pchangevalue<=minvalue):
                        headstock_value = headstock_value.tail(n=threshold)
                        lastexecutor=executor.submit(run_check,headstock_key,headstock_value,allstocks,date)
                    else:
                        p.update(leavecount - len(allstocks))
                        leavecount = len(allstocks)

                if lastexecutor is not None:
                   if lastexecutor.done():
                       _data_ = lastexecutor.result()
                       if _data_ is not None:
                           similardic[headstock_key]=_data_
                           [allstocks.pop(k) for k in _data_]
                       else:
                           if (pchangevalue>=maxvalue or pchangevalue<=minvalue):
                              similardicnone[headstock_key] = None

                       p.update(leavecount-len(allstocks))
                       leavecount = len(allstocks)

                       lastexecutor = None
                time.sleep(0.1)

        p.close()
        print(f"klineSimilar_corrcoef_job.run_check：{date} {len(similardic)} {len(similardicnone)}")
        #results = run_check(stocks_data)
        #if results is None:
        #    return

        #logging.info(f"klineSimilar_corrcoef_job.run_check：{date}")
        #return results
        #date_start, is_cache = trd.get_trade_hist_interval(date.strftime("%Y-%m-%d"))



    except Exception as e:
        logging.error(f"klineSimilar_corrcoef_job.prepare处理异常：{e}")


def run_check(headstock_key,compareStocks,stocks, date, workers=40):
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


def MA(S,N):              #求序列的N日简单移动平均值，返回序列
    return pd.Series(S).rolling(N).mean().values

def main():
    runt.run_with_args(prepare)

    # main函数入口
if __name__ == '__main__':
    main()