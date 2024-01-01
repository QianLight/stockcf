#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '

def check(code_name, data, date=None, threshold=1):
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

    amplitude_today = max(abs(data.iloc[-1]['quote_change']), abs(data.iloc[-1]['amplitude']))
    p_change = data.iloc[-1]['p_change']
    if amplitude_today>9.8 and p_change>0:
        return True
    else:
       return False
