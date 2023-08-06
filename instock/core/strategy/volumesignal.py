#!/usr/local/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


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

    desshow = f"{vol_ratio_lastday}:正"
    if p_change < 0:
        desshow = f"{vol_ratio_lastday}:负"
        #vol_ratio_lastday =-vol_ratio_lastday
        vol_ratio_mean =-vol_ratio_mean

    if abs(vol_ratio_lastday) >= 1.5:
        return True, desshow
    #if abs(vol_ratio_mean) >= 2:
    #    return True, vol_ratio_mean
    else:
        return False
