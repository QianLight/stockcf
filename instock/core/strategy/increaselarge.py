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

    mindata=data['low'].values.min()
    maxdata=data['max'].values.max()


    min_max = (maxdata - mindata) / maxdata

    if min_max>0.3:
        return True
    else:
       return False
