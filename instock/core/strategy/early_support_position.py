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
        data = data.loc[mask]

    if len(data) >= threshold:
        data = data.tail(n=threshold)
        data.reset_index(inplace=True, drop=True)

    result=checklow60(data)
    return result

def checklowup10(data):
    mask = (data['p_change'] >9.5)
    dataup10 = data.loc[mask].copy()
    if len(dataup10)<1:
        return False

    daymin = data.iloc[-1]['low']

    minallTime = dataup10['low'].values.min()

    daymin_low_ratio = round((daymin - minallTime) / minallTime, 2)
    low_index = data['low'].idxmin() + 1
    daymin_low_ratio_day = len(data) - low_index


    maxallTime = data['high'].values.max()
    daymin_max_ratio = round((maxallTime - daymin) / maxallTime, 2)
    max_index = data['high'].idxmax() + 1
    daymin_max_ratio_day = len(data) - max_index

    desshow = f"{daymin_low_ratio}:{daymin_low_ratio_day},{daymin_max_ratio}:{daymin_max_ratio_day}"
    if daymin_low_ratio <0.05:
        return True, desshow

    return False


def checkHasWave(data, upchange=10, waveminchange=4):
    regionwavechange_down = 0
    regionwavechange_up = 0

    regionwavestarthigh = 0
    regionwavechange = 0
    changeindex = 0


    isup = False

    wavehigh = []
    wavelow = []

    wavehighindex = []
    wavelowindex = []

    wavestartindex = len(data) -1

    waveindex = len(data) - 2
    while waveindex >= 0:
        #currentlow= data['low'].values[startindex]

        if  data['high'].values[waveindex]>data['high'].values[wavestartindex]:
            regionwavechange = (data['high'].values[waveindex] - data['low'].values[wavestartindex]) / data['low'].values[wavestartindex]
        else:
            regionwavechange = (data['high'].values[wavestartindex] - data['low'].values[waveindex]) / \
                               data['low'].values[wavestartindex]

        if regionwavechange > 0:
            if regionwavechange > regionwavechange_up:  # 持续上涨 记录上涨幅度
                regionwavechange_up = regionwavechange
            else:  # 假如不上涨 记录开始的时间
                changeindex = waveindex
                if regionwavechange_up - regionwavechange > waveminchange:  # 假如距离上次涨幅超过了小波震动 估计已经反转了
                    wavehighindex.append(changeindex + 1)
                    wavehigh.append(regionwavechange_up)
                    regionwavestartlow = data['low'].values[waveindex]
                    regionwavechange_up = 0

        elif regionwavechange < 0:
            if regionwavechange < regionwavechange_down:  # 持续下跌 记录上涨幅度
                regionwavechange_down = regionwavechange
            else:  # 假如不下跌 记录开始的时间
                changeindex = waveindex
                if regionwavechange - regionwavechange_down > waveminchange:  # 假如距离上次下跌超过了小波震动 估计已经反转了
                    wavelowindex.append(changeindex + 1)
                    wavelow.append(regionwavechange_down)
                    regionwavestartlow = data['low'].values[waveindex]
                    regionwavechange_down = 0

        waveindex -= 1

    if regionwavechange_up > 0:
        wavehigh.append(regionwavechange_up)
    elif regionwavechange_up < 0:
        wavelow.append(regionwavechange_up)

    return False

def checklow60(data):
    mask = (data['p_change'] >8)
    dataup5 = data.loc[mask].copy()
    if len(dataup5)<1:
        return False

    #datahigh=data.sort_values(by="high", inplace=False, ascending=True)
    #datalow = data.sort_values(by="low", inplace=False, ascending=True)

    daymin = data.iloc[-1]['low']

    minallTime = data['low'].values.min()

    daymin_low_ratio = round((daymin - minallTime) / daymin, 2)
    low_index = data['low'].idxmin() + 1
    daymin_low_ratio_day = len(data) - low_index


    maxallTime = data['high'].values.max()
    daymin_max_ratio = round((maxallTime - daymin) / maxallTime, 2)
    max_index = data['high'].idxmax() + 1
    daymin_max_ratio_day = len(data) - max_index

    desshow = f"{daymin_low_ratio}:{daymin_low_ratio_day},{daymin_max_ratio}:{daymin_max_ratio_day}"
    if daymin_low_ratio <0.05:
        return True, desshow

    return False


def check1(code_name, data, date=None, threshold=60):
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

    if data.iloc[-1]['p_change']<-9:#当天跌停不考虑
         return False

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