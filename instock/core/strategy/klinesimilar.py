#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_klinesimilar(comparedata,code_name, data, date=None, threshold=60):

    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    #if len(data.index) < threshold:
    #    return False

    #data = data.tail(n=threshold)

    for compareStocks in comparedata:
        targetlength=len(compareStocks)
        if len(data)<targetlength:
            continue
        datatoday = data.tail(n=targetlength)
        open_k = np.corrcoef(compareStocks['open'], datatoday['open'])[0][1]
        # /**-------------计算相关系数-------------------*/
        close_k = np.corrcoef(compareStocks['close'], datatoday['close'])[0][1]
        high_k = np.corrcoef(compareStocks['high'], datatoday['high'])[0][1]
        low_k = np.corrcoef(compareStocks['low'], datatoday['low'])[0][1]
        # ma5_k = np.corrcoef(compare_ma5, ma5_o)[0][1]
        ave_k = (open_k + close_k + high_k + low_k) / 4
        if ave_k > 0.5:
            des=compareStocks.iloc[0]["dynamic_para"]
            dynamic_parastr=f"{des}-{round(ave_k, 2)}"
            return True,dynamic_parastr
    return False
