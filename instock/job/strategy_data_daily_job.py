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
from instock.core.singleton_stock import stock_hist_data
from instock.core.stockfetch import fetch_stock_top_entity_data
from instock.job.klineSimilar_corrcoef_job import getklineComparedata

__author__ = 'myh '
__date__ = '2023/3/10 '


def prepare(date, strategy):
    try:
        stocks_data = stock_hist_data(date=date).get_data()
        if stocks_data is None:
            return
        table_name = strategy['name']
        strategy_func = strategy['func']
        results= run_check(strategy_func, table_name, stocks_data, date)
        if results is None:
            return

        if type(results) == tuple:
            results,results1=results

        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_STRATEGIES[0]['columns'])

        data = pd.DataFrame(results)
        columns = tuple(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])
        data.columns = columns
        if results1 is not None:
           data["dynamic_para"]=results1

        _columns_backtest = tuple(tbs.TABLE_CN_STOCK_BACKTEST_DATA['columns'])
        data = pd.concat([data, pd.DataFrame(columns=_columns_backtest)])
        # 单例，时间段循环必须改时间
        date_str = date.strftime("%Y-%m-%d")
        if date.strftime("%Y-%m-%d") != data.iloc[0]['date']:
            data['date'] = date_str
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
        print(f"strategy_data_daily_job save to databbase：{date} 策略 {table_name}")

    except Exception as e:
        logging.error(f"strategy_data_daily_job.prepare处理异常：{table_name}策略{e}")


def run_check(strategy_fun, table_name, stocks, date, workers=40):
    is_check_high_tight = False
    if strategy_fun.__name__ == 'check_high_tight':
        stock_tops = fetch_stock_top_entity_data(date)
        if stock_tops is not None:
            is_check_high_tight = True

    comparedata=None
    if strategy_fun.__name__ == 'check_klinesimilar':
        comparedata=getklineComparedata(stocks,date)

    data = []
    dynamicdata=[]
    nAllCounts=len(stocks)
    nBackIndex=0;

    des_tqdm =" 策略:"+table_name
    if date is not None:
        des_tqdm = date.strftime("%Y-%m-%d") + des_tqdm
    #p = tqdm(total=nAllCounts, desc=des_tqdm)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            if is_check_high_tight:
                future_to_data = {executor.submit(strategy_fun, k, stocks[k], date=date, istop=(k[1] in stock_tops)): k for k in stocks}
            else:
                if comparedata is None:
                    future_to_data = {executor.submit(strategy_fun, k, stocks[k], date=date): k for k in stocks}
                else:
                    future_to_data = {executor.submit(strategy_fun, comparedata,k, stocks[k], date=date): k for k in stocks}

            for future in concurrent.futures.as_completed(future_to_data):
                stock = future_to_data[future]
                try:
                    _data_ = future.result()
                    if _data_:
                        data.append(stock)
                        if type(_data_) == tuple:
                            dynamicdata.append(_data_[1])
                        else:
                            dynamicdata.append("")

                    nBackIndex+=1
                    #p.update(1)
                    #print(f"strategy_fun.Back：future {date} {stock[2]}  {nBackIndex}/ {nAllCounts}")

                except Exception as e:
                    logging.error(f"strategy_data_daily_job.run_check处理异常：{stock[1]}代码{e}策略{table_name}")
    except Exception as e:
        logging.error(f"strategy_data_daily_job.run_check处理异常：{e}策略{table_name}")

    #p.close()
    if not data:
        return None
    else:
        return data,dynamicdata


def main(strategyindex=-1):
    # 使用方法传递。
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if strategyindex>=0:
            executor.submit(runt.run_with_args, prepare, tbs.TABLE_CN_STOCK_STRATEGIES[strategyindex])
        else:
            for strategy in tbs.TABLE_CN_STOCK_STRATEGIES:
                executor.submit(runt.run_with_args, prepare, strategy)
            #startindex=0;
            #totalindex=len(tbs.TABLE_CN_STOCK_STRATEGIES)
            #lastexecutor = None
            #while startindex <= totalindex:
            #    if lastexecutor is None:
            #        lastexecutor=executor.submit(runt.run_with_args, prepare, tbs.TABLE_CN_STOCK_STRATEGIES[startindex])
            #    if lastexecutor is not None:
            #       if lastexecutor.done():
            #            startindex+=1
            #            lastexecutor = None

            #    time.sleep(0.1)


# main函数入口
if __name__ == '__main__':
    main()
