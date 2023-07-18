#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import concurrent.futures
import instock.core.stockfetch as stf
import instock.core.tablestructure as tbs
import instock.lib.trade_time as trd
from instock.lib.singleton_type import singleton_type
from tqdm import tqdm

__author__ = 'myh '
__date__ = '2023/3/10 '


# 读取当天股票数据
class stock_data(metaclass=singleton_type):
    def __init__(self, date):
        try:
            self.data = stf.fetch_stocks(date)
        except Exception as e:
            logging.error(f"singleton.stock_data处理异常：{e}")

    def get_data(self):
        return self.data


# 读取股票历史数据
class stock_hist_data(metaclass=singleton_type):
    def __init__(self, next_day=None,date=None, stocks=None, workers=16):
        if stocks is None:
            _allDatas=stock_data(date).get_data()
            _subset = _allDatas[list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])]
            stocks = [tuple(x) for x in _subset.values]
            stockAllDatas = [tuple(x) for x in _allDatas.values]

        if stocks is None:
            self.data = None
            return
        date_start, is_cache = trd.get_trade_hist_interval(stocks[0][0])  # 提高运行效率，只运行一次
        _data = {}

        nAllCounts = len(stocks)
        nBackIndex = 0;

        des_tqdm=" 历史数据"
        if date is not None:
            des_tqdm=date.strftime("%Y-%m-%d")+des_tqdm

        p = tqdm(total=nAllCounts,desc=des_tqdm)

        #print(f"stock_hist_data.Back：start {date} {nAllCounts}")

        try:
            # max_workers是None还是没有给出，将默认为机器cup个数*5
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_stock = {executor.submit(stf.fetch_stock_hist, stock,stockAllData, date_start, is_cache,next_day=next_day): stock for stock,stockAllData
                                   in zip(stocks,stockAllDatas)}
                for future in concurrent.futures.as_completed(future_to_stock):
                    stock = future_to_stock[future]
                    try:
                        __data = future.result()
                        if __data is not None:
                            _data[stock] = __data

                        nBackIndex += 1
                        p.update(1)
                        #print(f"stock_hist_data.Back：future {date} {stock[2]}  {nBackIndex}/ {nAllCounts}")
                    except Exception as e:
                        logging.error(f"singleton.stock_hist_data处理异常：{stock[1]}代码{e}")
        except Exception as e:
            logging.error(f"singleton.stock_hist_data处理异常：{e}")
        if not _data:
            self.data = None
        else:
            self.data = _data

    def get_data(self):
        return self.data
