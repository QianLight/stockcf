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

    data = data.tail(n=threshold+1)
    minvalue=data.head(n=60)['low'].values.min()
    daymin=data.iloc[-1]['low']
    #if daymin<=minvalue:
    #   return True

    cup_height_ratio = 0.2  # 杯部相对高度阈值
    handle_height_ratio = 0.1  # 柄部相对高度阈值
    #if find_cup_handle(data,cup_height_ratio,handle_height_ratio):
    #    return True
    return False


def find_cup_handle(data, cup_height_ratio, handle_height_ratio):
    data['Cup'] = False
    data['Handle'] = False

    isFitCup=False
    isFitHandle = False
    i=len(data) - 2
    #for i in range(2, len(data) - 2):
    # 判断是否满足杯部条件
    if data['low'][i] < data['low'][i-1] and data['low'][i] < data['low'][i-2]:
        if data['high'][i] > data['high'][i-1] and data['high'][i] > data['high'][i-2]:
            cup_height = data['high'][i] - data['low'][i]
            if cup_height <= (cup_height_ratio * max(data['high'][i-2:i+1])):
                isFitCup = True

    # 判断是否满足柄部条件
    if data['low'][i] > data['low'][i-1] and data['low'][i] > data['low'][i-2]:
        if data['high'][i] < data['high'][i-1] and data['high'][i] < data['high'][i-2]:
            handle_height = data['high'][i] - data['low'][i]
            if handle_height <= (handle_height_ratio * max(data['high'][i-2:i+1])):
                isFitHandle = True

    return isFitCup and isFitHandle

# 设定股票代码和相对高度阈值
ticker = "AAPL"
cup_height_ratio = 0.2  # 杯部相对高度阈值
handle_height_ratio = 0.1  # 柄部相对高度阈值


