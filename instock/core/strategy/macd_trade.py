#!/usr/local/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


# 放量跌停
# 1.跌>9.5%
# 2.成交额不低于2亿
# 3.成交量至少是5日平均成交量的4倍
def check(code_name, data, date=None, threshold=30):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)

    # macd
    data.loc[:, 'macd'], data.loc[:, 'macds'], data.loc[:, 'macdh'] = tl.MACD(
        data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    data['macd'].values[np.isnan(data['macd'].values)] = 0.0
    data['macds'].values[np.isnan(data['macds'].values)] = 0.0
    data['macdh'].values[np.isnan(data['macdh'].values)] = 0.0




