#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import logging
import concurrent.futures
import pandas as pd
import os.path
import sys
import time
from tqdm import tqdm

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.lib.run_template as runt
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.core.indicator.calculate_indicator as idr
from instock.core.singleton_stock import stock_hist_data

__author__ = 'myh '
__date__ = '2023/3/10 '


def prepare(date):
    try:
        stocks_data = stock_hist_data(date=date).get_data()

        if stocks_data is None:
            return
        results = run_check(stocks_data, date=date)
        if results is None:
            return
        allDatas = pd.concat(results)
        qlibTargetFolder = F'F:/Project/Gits/ProjectData/cfquant/'
        trainname="train"
        #if utilsHelper.CheckIsHouse() == True:
        qlibTargetFolder = F'H:/Stock/ProjectData/qlibdata/'

        exportPath = f'{qlibTargetFolder}{trainname}.csv'
        allDatas.to_csv(exportPath, index=False)


    except Exception as e:
        logging.error(f"indicators_data_daily_job.prepare处理异常：{e}")


def run_check(stocks, date=None, workers=40):
    data = []
    columns = list(tbs.STOCK_STATS_DATA['columns'])
    columns.insert(0, 'code')
    columns.insert(0, 'date')
    data_column = columns

    #print(f"run_check get_indicator {date}")

    nAllCounts=len(stocks)
    nBackIndex=0;
    p = tqdm(total=nAllCounts, desc=date.strftime("%Y-%m-%d")+" 指标计算")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_data = {executor.submit(idr.get_indicator, k, stocks[k], data_column, date=date,threshold=None,calc_threshold=None): k for k in stocks}
            for future in concurrent.futures.as_completed(future_to_data):
                stock = future_to_data[future]
                try:
                    _data_ = future.result()

                    if _data_ is not None:
                        #data[stock] = _data_
                        data.append(_data_)

                    nBackIndex+=1
                    p.update(1)
                    #print(f"calculate_indicator.Back：future {date} {stock[2]}  {nBackIndex}/ {nAllCounts}")
                except Exception as e:
                    logging.error(f"indicators_data_daily_job.run_check处理异常：{stock[1]}代码{e}")
    except Exception as e:
        logging.error(f"indicators_data_daily_job.run_check处理异常：{e}")
    if not data:
        return None
    else:
        return data




def main():
    # 使用方法传递。
    runt.run_with_args(prepare)


# main函数入口
if __name__ == '__main__':
    main()
