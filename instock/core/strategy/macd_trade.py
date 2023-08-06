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
def check(code_name, data, date=None, threshold=7):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    #data = data.tail(n=threshold)

    # macd
    data.loc[:, 'macd'], data.loc[:, 'macds'], data.loc[:, 'macdh'] = tl.MACD(
        data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    data['macd'].values[np.isnan(data['macd'].values)] = 0.0
    data['macds'].values[np.isnan(data['macds'].values)] = 0.0
    data['macdh'].values[np.isnan(data['macdh'].values)] = 0.0

    macd_today = data.iloc[-1]['macdh']
    macd_lastday = data.iloc[-2]['macdh']

    macd7 = data.tail(n=7)
    macd7_mean=macd7['macdh'].values.mean()

    # kdjk
    data.loc[:, 'kdjk'], data.loc[:, 'kdjd'] = tl.STOCH(
        data['high'].values, data['low'].values, data['close'].values, fastk_period=9,
        slowk_period=5, slowk_matype=1, slowd_period=5, slowd_matype=1)
    data['kdjk'].values[np.isnan(data['kdjk'].values)] = 0.0
    data['kdjd'].values[np.isnan(data['kdjd'].values)] = 0.0
    data.loc[:, 'kdjj'] = 3 * data['kdjk'].values - 2 * data['kdjd'].values

    kdjj_min = data['kdjj'].values.min()
    kdjd_today = data.iloc[-1]['kdjd']
    kdjk_today = data.iloc[-1]['kdjk']
    kdjj_today = data.iloc[-1]['kdjj']

    kdjjratio=round((kdjj_today-kdjj_min)/kdjj_min,2)

    #if macd_lastday <= 0 <= macd_today:
    #    return True,macd7_mean
    #if kdjjratio<=0.1:
    #    return True,kdjjratio
    #if abs(macd_today)<=0.05 and abs(kdjd_today-kdjk_today)<1:
    #    return True

    if checkopenclose(data.iloc[-1],data.iloc[-2]) and checkopenclose(data.iloc[-2],data.iloc[-3]):
        return True

    return False


def checkopenclose(today,lastday):
    if today["close"]>lastday["close"] and today["open"]>lastday["open"]:
        return True
    return False
