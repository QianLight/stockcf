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

    if len(data.index) > 180:
        return False

    if len(data)==0:
        return False

    if data.iloc[-1]['p_change']>9.8:
        return True
    #mask = (data['p_change'] >9.5)
    #dataup10 = data.loc[mask].copy()
    #if len(dataup10)<1:
    #    return False


    return False
