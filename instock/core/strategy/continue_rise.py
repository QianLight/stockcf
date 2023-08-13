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

    daychange1 = data.iloc[-1]['p_change']
    daychange2 = data.iloc[-2]['p_change']
    daychange3 = data.iloc[-3]['p_change']

    if daychange1>0 and daychange2>0 and daychange3<0 and (daychange1+daychange2)<10:
        return True

    return False