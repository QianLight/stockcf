#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import concurrent.futures
import instock.core.stockfetch as stf
import instock.core.tablestructure as tbs
import instock.lib.trade_time as trd
from instock.lib.singleton_type import singleton_type
from tqdm import tqdm
from operator import itemgetter
import numpy as np
import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '


# 读取当天股票数据
class stock_data(metaclass=singleton_type):
    def __init__(self, date):
        try:
            self.data = stf.fetch_stocks(date)
            self.data_hy=stf.fetch_stocks_sector_fund_flow(1,0)

        except Exception as e:
            logging.error(f"singleton.stock_data处理异常：{e}")

    def get_data(self):
        return self.data

    def get_data_hy(self):
        return self.data_hy


# 读取股票历史数据
class stock_hist_data(metaclass=singleton_type):
    def __init__(self, next_day=None,date=None, stocks=None, workers=16):
        if stocks is None:
            _allDatas=stock_data(date).get_data()
            _subset = _allDatas[list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])]
            stocks = [tuple(x) for x in _subset.values]
            stockAllDatas = [tuple(x) for x in _allDatas.values]

        self.make_hy_data(next_day=next_day,date=date,stocks=stocks,workers=workers)
        self.make_stocks(alldatas=stockAllDatas,stocks=stocks,next_day=next_day,date=date,workers=workers)
        self.caculate_hy_data()

    def make_stocks(self,alldatas,stocks,next_day=None,date=None,workers=16):

         if stocks is None:
            self.data = None
            self.datacode= None
            return

         date_start, is_cache = trd.get_trade_hist_interval(stocks[0][0])  # 提高运行效率，只运行一次
         _data = {}
         _datacode={}

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
                 future_to_stock = {executor.submit(stf.fetch_stock_hist, stock, stockAllData, date_start, is_cache,
                                                    next_day=next_day): stock for stock, stockAllData
                                    in zip(stocks, alldatas)}
                 for future in concurrent.futures.as_completed(future_to_stock):
                     stock = future_to_stock[future]
                     try:
                         __data = future.result()
                         if __data is not None:
                             _data[stock] = __data
                             _datacode[stock[1]]=__data

                         nBackIndex += 1
                         p.update(1)
                         # print(f"stock_hist_data.Back：future {date} {stock[2]}  {nBackIndex}/ {nAllCounts}")
                     except Exception as e:
                         logging.error(f"singleton.stock_hist_data处理异常：{stock[1]}代码{e}")
         except Exception as e:
             logging.error(f"singleton.stock_hist_data处理异常：{e}")
         if not _data:
             self.data = None
             self.datacode = None
         else:
             self.data = _data
             self.datacode = _datacode


    def make_hy_data(self,next_day=None,date=None,stocks=None,workers=16):
         if stocks is None:
             self.data_hy = None
             return

         dateStock=stocks[0][0]
         date_start, is_cache = trd.get_trade_hist_interval(dateStock)  # 提高运行效率，只运行一次
         stocks=stock_data(date).get_data_hy()
         stocks =[tuple(x) for x in stocks.values]
         _data_hy = {}

         nAllCounts = len(stocks)
         nBackIndex = 0;

         des_tqdm = " 获取概念"
         if date is not None:
             des_tqdm = date.strftime("%Y-%m-%d") + des_tqdm
         p = tqdm(total=nAllCounts, desc=des_tqdm)

         try:
             # max_workers是None还是没有给出，将默认为机器cup个数*5
             with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                 future_to_stock = {executor.submit(stf.fetch_stock_hy,stock,date_start, is_cache,
                                                    next_day=next_day): stock for stock
                                    in zip(stocks)}

                 for future in concurrent.futures.as_completed(future_to_stock):
                     stock = future_to_stock[future]
                     try:
                         __data = future.result()
                         if __data is not None:
                             _data_hy[stock] = __data

                         nBackIndex += 1
                         p.update(1)

                     except Exception as e:
                         logging.error(f"singleton.make_by_data 处理异常：{stock[1]}代码{e}")
         except Exception as e:
             logging.error(f"singleton.make_by_data 处理异常：{e}")
         if not _data_hy:
             self.data_hy = None
         else:
             self.data_hy = _data_hy

         p.close()


    def caculate_hy_data(self,workers=16):

        keytime=list(self.data.keys())[0][0]
        des_tqdm = " 计算概念均值"
        p = tqdm(total=len(self.data_hy), desc=des_tqdm)

        try:
            # max_workers是None还是没有给出，将默认为机器cup个数*5
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_stock = {executor.submit(self.caculate_hy_data_thread, data_hy_key, data_hy_value): data_hy_key
                                   for (data_hy_key, data_hy_value)
                                   in self.data_hy.items()}

                for future in concurrent.futures.as_completed(future_to_stock):
                    stock = future_to_stock[future]
                    try:
                        __data = future.result()
                        if __data is not None:
                            code = stock[0][0]
                            industry = stock[0][1]
                            dictKey = tuple([keytime, code, industry, industry])
                            self.data[dictKey] = __data
                        p.update(1)

                    except Exception as e:
                        logging.error(f"singleton.make_by_data 处理异常：{stock[1]}代码{e}")
        except Exception as e:
            logging.error(f"singleton.make_by_data 处理异常：{e}")
        p.close()

    def caculate_hy_data_thread(self,data_hy_key, data_hy_value):
        code=data_hy_key[0][0]
        industry=data_hy_key[0][1]
        itmdata=[]
        for conceptcode in data_hy_value["code"].values:
            if conceptcode in self.datacode:
                itmdata.append(self.datacode[conceptcode])

        if len(itmdata)==0:
            return None

        itmdataframe = pd.concat(itmdata)
        #itmdataframe.drop(['industry'], axis=1, inplace=True)
        datadate = itmdataframe.groupby('date')
        #newdaymean=[]
        datadatemean=datadate.mean()
        datadatemean.insert(datadatemean.shape[1] - 1, "industry", "BK"+industry)
        datakeys=datadatemean.index.values
        datadatemean.insert(0, "date", datakeys)
        datadatemean.reset_index(inplace=True, drop=True)
        #for date, group in datadate:
        #    avgs=pd.DataFrame(group.mean()).T
        #    avgs.insert(0,"date", date)
        #    avgs.insert(avgs.shape[1]-1, "industry", industry)
            #newdaymean.append(avgs)

        #newdaymean=pd.concat(newdaymean)
        return datadatemean


    def get_data(self):
        return self.data
