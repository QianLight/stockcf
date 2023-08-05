#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


# 持续上涨（MA30向上）
# 均线多头
# 1.30日前的30日均线<20日前的30日均线<10日前的30日均线<当日的30日均线
# 3.(当日的30日均线/30日前的30日均线)>1.2
def check(code_name, data, date=None, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    data.loc[:, 'ma5'] = tl.MA(data['close'].values, timeperiod=5)
    data['ma5'].values[np.isnan(data['ma5'].values)] = 0.0

    data.loc[:, 'ma10'] = tl.MA(data['close'].values, timeperiod=10)
    data['ma10'].values[np.isnan(data['ma10'].values)] = 0.0

    data.loc[:, 'ma20'] = tl.MA(data['close'].values, timeperiod=20)
    data['ma20'].values[np.isnan(data['ma20'].values)] = 0.0

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    mean5 = data.iloc[-1]['ma5']
    mean10= data.iloc[-1]['ma10']
    mean20= data.iloc[-1]['ma20']
    mean30= data.iloc[-1]['ma30']

    if mean5>=mean10 and mean5>=mean20 and data.iloc[-2]['ma5']<=data.iloc[-2]['ma10']:
        return True,code_name[2]
    else:
        return False



    #if mean5>mean10 and mean5>mean20 and mean5>mean30 and mean10>mean20:
    #    return True,code_name[2]
    #else:
    #    return False
