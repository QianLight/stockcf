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

    #if len(data.index) < 90:
    #    return False

    maxallTime=data['high'].values.max()
    minallTime = data['low'].values.min()
    daymin = data.iloc[-1]['low']
    lowratio = (daymin - minallTime) / minallTime
    if lowratio <= 0.01:#近三年所有时间新低
        return True

    threshold=180
    if len(data.index) > threshold+1:
        datatail = data.tail(n=threshold+1)
        minvalue=datatail.head(n=threshold)['low'].values.min()
        daymin=datatail.iloc[-1]['low']
        if daymin<=minvalue:
           return True

        lowratio=(daymin-minvalue)/minvalue
        if lowratio<=0.01:
           return True
    #middleIndex=-3
    #if data.iloc[middleIndex]['low'] < data.iloc[middleIndex-1]['low'] and data.iloc[middleIndex]['low'] < data.iloc[middleIndex-2]['low'] and \
    #        data.iloc[middleIndex]['low'] < data.iloc[middleIndex+1]['low'] and data.iloc[middleIndex]['low'] < data.iloc[middleIndex+2]['low']:
    #    return True

    return False
