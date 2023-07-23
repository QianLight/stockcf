#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl
from datetime import datetime, timedelta

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()

    if len(data.index) < 90:
        return False

    if data.iloc[-1]['industry'].startswith("BK"):
        return False
    datayear = data.tail(360)
    data = data.tail(n=threshold)

    if checkHas20_30(data)==False:
        return False

    if checkHasLower(datayear)==False:
        return False

    if checkHasContinueLargeDown(data,4,-10,10)==True:
        return False

    hasLarge5=checkHasLarge5(data)
    hasContinueRise=checkHasContinueRise(data,4,5)

    if hasLarge5 or hasContinueRise:
        return True

    return False


def checkHasLarge5(data):
    maxchange=data['p_change'].values.max()
    if maxchange<5:
        return False
    return True

def checkHas20_30(data):
    data.loc[:, 'ma20'] = tl.MA(data['close'].values, timeperiod=20)
    data['ma20'].values[np.isnan(data['ma20'].values)] = 0.0

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    mean20= data.iloc[-1]['ma20']
    mean30= data.iloc[-1]['ma30']
    if abs(mean20-mean30)>0.1:
        return  False
    return True

def checkHasContinueRise(data,min_rebound_points,totalchange):
    for i in range(len(data)-1,1,-1):
        # 判断是否满足第一个低点条件
        if data['p_change'].values[i] >0:
            j = i
            rebound_points = 0
            changedata=0
            # 统计反弹的点数
            while j > 0 and data['p_change'].values[j]>0:
                rebound_points += 1
                changedata+=data['p_change'].values[j]
                j -= 1

            if rebound_points >= min_rebound_points and changedata>=totalchange:
                return True

    return False

def checkHasContinueLargeDown(data,min_rebound_points,totalchange,beforeday):#是否存在大且急的抛  但是要发生在十天前吧
    for i in range(len(data)-1,1,-1):
        # 判断是否满足第一个低点条件
        if data['p_change'].values[i] <0:
            j = i
            rebound_points = 0
            changedata=0
            # 统计抛的点数
            while j > 0 and data['p_change'].values[j]<0:
                rebound_points += 1
                changedata+=data['p_change'].values[j]
                j -= 1

                if rebound_points >= min_rebound_points and changedata<totalchange and len(data)-j<beforeday:
                    return True

    return False

def checkHasLower(data):
    minvalue = data.head(n=len(data)-1)['low'].values.min()
    daymin = data.iloc[-1]['low']
    if daymin <= minvalue:
        return True

    lowratio = (daymin - minvalue) / minvalue
    if lowratio <= 0.01:
        return True
    return False