#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl
from datetime import datetime, timedelta

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(code_name, data, date=None, threshold=15):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()

    if len(data.index) < 90:
        return False

    data = data.tail(n=threshold)
    mask = (data['amplitude'] >5)
    data5 = data.loc[mask].copy()
    ratio=len(data5)/len(data)

    daychange = data.iloc[-1]['p_change']
    if ratio>0.5 and daychange<1:
        return True

    return False

