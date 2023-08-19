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

    daychange1 = data.iloc[-1]['amplitude']
    daychange2 = data.iloc[-2]['amplitude']
    daychange3 = data.iloc[-3]['amplitude']

    if abs(daychange1)<1 and abs(daychange2)<1 and abs(daychange3)<1:
        return True

    return False