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

    min_rebound_points = 3  # 反弹点数阈值，指反弹的连续点数
    if find_double_bottom(data,min_rebound_points):
        return True
    return False


def find_double_bottom(data, min_rebound_points):
    for i in range(len(data)-2,1,-1):
        # 判断是否满足第一个低点条件
        if data['low'][i] < data['low'][i-1] and data['low'][i] < data['low'][i+1]:
            j = i
            rebound_points = 0
            # 统计反弹的点数
            while j > 0 and data['low'][j] < data['low'][j-1]:
                rebound_points += 1
                j -= 1
            j = i
            while j < len(data) - 1 and data['low'][j] < data['low'][j+1]:
                rebound_points += 1
                j += 1

            if rebound_points >= min_rebound_points:
                return True

    return False



