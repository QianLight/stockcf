#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import logging
import concurrent.futures
import pandas as pd
import os.path
import sys
import datetime
import time

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.core.backtest.rate_stats as rate
from instock.core.singleton_stock import stock_hist_data
from tqdm import tqdm

__author__ = 'myh '
__date__ = '2023/3/10 '


# 股票策略回归测试。
def prepare(targetindex=-1):
    tables = [tbs.TABLE_CN_STOCK_INDICATORS_BUY, tbs.TABLE_CN_STOCK_INDICATORS_SELL]
    tables.extend(tbs.TABLE_CN_STOCK_STRATEGIES)
    backtest_columns = list(tbs.TABLE_CN_STOCK_BACKTEST_DATA['columns'])
    backtest_columns.insert(0, 'code')
    backtest_columns.insert(0, 'date')
    backtest_column = backtest_columns

    stocks_data = stock_hist_data().get_data()
    if stocks_data is None:
        return
    for k in stocks_data:
        date = k[0]
        break
    print(f"backtest_data_daily_job 表数量 {len(tables)}")
    # 回归测试表
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if targetindex>=0:
            executor.submit(process, tables[0], stocks_data, date, backtest_column)
            executor.submit(process, tables[1], stocks_data, date, backtest_column)
            executor.submit(process, tables[2], stocks_data, date, backtest_column)
        else:
            for table in tables:
                executor.submit(process, table, stocks_data, date, backtest_column)


def process(table, data_all, date, backtest_column):
    table_name = table['name']
    start = datetime.datetime.now()
    if not mdb.checkTableIsExist(table_name):
        return

    column_tail = tuple(table['columns'])[-1]
    now_date = datetime.datetime.now().date()
    sql = f"SELECT * FROM `{table_name}` WHERE `date` < '{now_date}' AND `{column_tail}` is NULL"
    try:
        data = pd.read_sql(sql=sql, con=mdb.engine())
        if data is None or len(data.index) == 0:
            return

        data['dynamic_para']=''
        subset = data[list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])]
        # subset['date'] = subset['date'].values.astype('str')
        subset = subset.astype({'date': 'string'})
        stocks = [tuple(x) for x in subset.values]

        results = run_check(stocks, data_all, date, backtest_column)
        if results is None:
            return

        data_new = pd.DataFrame(results.values())
        mdb.update_db_from_df(data_new, table_name, ('date', 'code'))
        print(f"backtest_data_daily_job：{date}  表 {table_name} {datetime.datetime.now() - start}")
    except Exception as e:
        logging.error(f"backtest_data_daily_job.process处理异常：{table_name}表{e}")


def run_check(stocks, data_all, date, backtest_column, workers=40):
    data = {}

    nAllCounts=len(stocks)
    nBackIndex=0;

    des_tqdm = " 回测"
    if date is not None:
        des_tqdm = date + des_tqdm
    #p = tqdm(total=nAllCounts, desc=des_tqdm)

    #for stock in stocks:
    #    keydata=(date, stock[1], stock[2], stock[3],stock[4])
    #    select=data_all.get(keydata)
    #    rate.get_rates(stock,select,backtest_column, len(backtest_column) - 1)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_data = {executor.submit(rate.get_rates, stock,
                                              data_all.get((date, stock[1], stock[2], stock[3],stock[4])), backtest_column,
                                              len(backtest_column) - 1): stock for stock in stocks}
            for future in concurrent.futures.as_completed(future_to_data):
                stock = future_to_data[future]
                try:
                    _data_ = future.result()
                    if _data_ is not None:
                        data[stock] = _data_

                    nBackIndex+=1
                    #p.update(1)
                    #print(f"backtest_data_daily_job.Back：future {date} {stock[2]}  {nBackIndex}/ {nAllCounts}")

                except Exception as e:
                    logging.error(f"backtest_data_daily_job.run_check处理异常：{stock[1]}代码{e}")
    except Exception as e:
        logging.error(f"backtest_data_daily_job.run_check处理异常：{e}")
   # p.close()
    if not data:
        return None
    else:
        return data


def main(targetindex=-1):
    prepare(targetindex)


# main函数入口
if __name__ == '__main__':
    main()
