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

    if data.iloc[-1]['quote_change']>9.8:
        return False

    if data.iloc[-1]['quote_change']<-9.8:
        return False

    uptrade = data.loc[(data['quote_change']>0)]
    downtrade = data.loc[(data['quote_change']<0)]

    if len(uptrade)>len(downtrade):
        return True
    else:
       return False
