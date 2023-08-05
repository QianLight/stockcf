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
    volumeav = data['volume'].values.mean()

    vol_ratio_lastday = round(data.iloc[-1]['volume'] / data.iloc[-2]['volume'], 2)
    vol_ratio_mean = round(data.iloc[-1]['volume'] / volumeav, 2)
    p_change = data.iloc[-1]['p_change']
    if p_change < 0:
        vol_ratio_lastday -= vol_ratio_lastday
        vol_ratio_mean -= vol_ratio_mean

    if abs(vol_ratio_lastday) >= 2:
        return True, vol_ratio_lastday
    if abs(vol_ratio_mean) >= 2:
        return True, vol_ratio_mean
    else:
        return False
