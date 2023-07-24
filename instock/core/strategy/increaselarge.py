#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '

def check(code_name, data, date=None, threshold=2):
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

    if data.iloc[-1]['p_change']>5 and data.iloc[-2]['p_change']<9.5:
        return True

    #if data.iloc[-1]['p_change']<0:
    #    return False

    #mindata=data.iloc[-1]['open']
    #maxdata=data.iloc[-1]['high']


    #min_max = (maxdata - mindata) / maxdata

    #if min_max>0.05:
    #    return True
    #else:
    return False
