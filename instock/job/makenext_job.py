#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os.path
import sys
import pandas as pd

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
from instock.core.singleton_stock import stock_hist_data

import datetime

__author__ = 'myh '
__date__ = '2023/3/10 '


# 股票实时行情数据。
def save_next_stock_data(date,next_day):
    # 股票列表
    try:
        stocks_data = stock_hist_data(date=date,next_day=next_day).get_data()
    except Exception as e:
        logging.error(f"save_next_stock_data.stock_hist_data处理异常：{e}")





def main():
    now_time = datetime.datetime.now()
    now_date = now_time.date()
    next_day = now_date#+datetime.timedelta(days=1)
    save_next_stock_data(now_date,next_day)


# main函数入口
if __name__ == '__main__':
    main()
