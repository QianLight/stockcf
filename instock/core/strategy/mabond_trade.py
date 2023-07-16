#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=180):
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

    data.loc[:, 'ma5'] = tl.MA(data['close'].values, timeperiod=5)
    data['ma5'].values[np.isnan(data['ma5'].values)] = 0.0

    data.loc[:, 'ma10'] = tl.MA(data['close'].values, timeperiod=10)
    data['ma10'].values[np.isnan(data['ma10'].values)] = 0.0

    data.loc[:, 'ma20'] = tl.MA(data['close'].values, timeperiod=20)
    data['ma20'].values[np.isnan(data['ma20'].values)] = 0.0

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    data.loc[:, 'ma60'] = tl.MA(data['close'].values, timeperiod=60)
    data['ma60'].values[np.isnan(data['ma60'].values)] = 0.0

    data.loc[:, 'ma120'] = tl.MA(data['close'].values, timeperiod=120)
    data['ma120'].values[np.isnan(data['ma120'].values)] = 0.0

    mean5 = data.iloc[-1]['ma5']
    mean10= data.iloc[-1]['ma10']
    mean20= data.iloc[-1]['ma20']
    mean30= data.iloc[-1]['ma30']
    mean60 = data.iloc[-1]['ma60']
    mean120 = data.iloc[-1]['ma120']



    mean5_10=(mean5-mean10)/mean10

    mean10_20=(mean10-mean20)/mean20
    mean10_30 = (mean10 - mean30) / mean30
    mean10_60 = abs(mean10 - mean60) / mean60
    mean10_120 = abs(mean10 - mean120) / mean120
    mean20_30 = abs(mean20 - mean30) / mean30
    mean20_60 = abs(mean20 - mean60) / mean60

    #if mean20>mean5 and

    targetValue=0.02
    if abs(mean10_20) <=targetValue and  abs(mean10_30) <=targetValue and  mean10_60 < targetValue and \
            mean10_120 < targetValue and \
            mean20_60 < targetValue and \
            mean20_30<targetValue:
        return True
    else:
       return False
