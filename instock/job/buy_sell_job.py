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

# 对每日指标数据，进行筛选。将符合条件的。二次筛选出来。
# 只是做简单筛选
def guess_buy(date):
    try:
        _table_name = tbs.TABLE_CN_STOCK_INDICATORS['name']
        if not mdb.checkTableIsExist(_table_name):
            return

        _columns = tuple(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])
        _selcol = '`,`'.join(_columns)

        data=FallDownToMuch(_selcol,_table_name,date)
        # data.set_index('code', inplace=True)
        if len(data.index) == 0:
            return

        table_name = tbs.TABLE_CN_STOCK_INDICATORS_BUY['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_INDICATORS_BUY['columns'])

        _columns_backtest = tuple(tbs.TABLE_CN_STOCK_BACKTEST_DATA['columns'])
        data = pd.concat([data, pd.DataFrame(columns=_columns_backtest)])
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
    except Exception as e:
        logging.error(f"indicators_data_daily_job.guess_buy处理异常：{e}")


def FallDownToMuch(_selcol,_table_name,date):

    sql = f'''SELECT `{_selcol}` FROM `{_table_name}` WHERE `date` = '{date}' and 
            `kdjk` < 20 and `kdjd` < 30 and 
            `cci` < -100 and `cr` < 40 and `wr_6` < -80 and `macd`<0 '''
    indicators_data = pd.read_sql(sql=sql, con=mdb.engine())
    indicators_data = indicators_data.drop_duplicates(subset="code", keep="last")

    sql = f'''SELECT `{_selcol}` FROM `{_table_name}` WHERE `date` = '{date}' and 
            `kdjk` < 10 and `kdjd` < 15 and `kdjj` < -1 and
            `cci` < -100 and `cr` < 40 and `wr_6` < -80 and `macd`<0 '''
    indicators_kdj1_data = pd.read_sql(sql=sql, con=mdb.engine())
    indicators_kdj1_data = indicators_kdj1_data.drop_duplicates(subset="code", keep="last")

    _table_name="cn_stock_strategy_lowdow60day_trade"
    sql = f'''SELECT `{_selcol}` FROM `{_table_name}` WHERE `date` = '{date}' '''
    lowdow60day_data = pd.read_sql(sql=sql, con=mdb.engine())
    lowdow60day_data = lowdow60day_data.drop_duplicates(subset="code", keep="last")

    fitdata=[]
    mask = (indicators_data['code'] .isin(lowdow60day_data["code"].values))
    fitdata.append(indicators_data.loc[mask].copy())

    #fitdata.append(indicators_kdj1_data)

    finaldata=pd.concat(fitdata)
    finaldata=finaldata.drop_duplicates(subset="code", keep="last")
    return finaldata

# 设置卖出数据。
def guess_sell(date):
    try:
        _table_name = tbs.TABLE_CN_STOCK_INDICATORS['name']
        if not mdb.checkTableIsExist(_table_name):
            return

        _columns = tuple(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])
        _selcol = '`,`'.join(_columns)
        sql = f'''SELECT `{_selcol}` FROM `{_table_name}` WHERE `date` = '{date}' and 
                `kdjk` >= 80 and `kdjd` >= 70 and `kdjj` >= 100 and `rsi_6` >= 80 and 
                `cci` >= 100 and `cr` >= 300 and `wr_6` >= -20 and `vr` >= 160'''
        data = pd.read_sql(sql=sql, con=mdb.engine())
        data = data.drop_duplicates(subset="code", keep="last")
        # data.set_index('code', inplace=True)
        if len(data.index) == 0:
            return

        table_name = tbs.TABLE_CN_STOCK_INDICATORS_SELL['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_INDICATORS_SELL['columns'])

        _columns_backtest = tuple(tbs.TABLE_CN_STOCK_BACKTEST_DATA['columns'])
        data = pd.concat([data, pd.DataFrame(columns=_columns_backtest)])
        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
    except Exception as e:
        logging.error(f"indicators_data_daily_job.guess_sell处理异常：{e}")


def main(caculateindicators=True):
    # 二次筛选数据。直接计算买卖股票数据。
    runt.run_with_args(guess_buy)
    runt.run_with_args(guess_sell)


# main函数入口
if __name__ == '__main__':
    main()
