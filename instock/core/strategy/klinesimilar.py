#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import talib as tl
import instock.core.kline.klineSimilar_corrcoef as corrcoef

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
    corrcoef.caculatema5(data)

    maxk=-2
    mink=100
    desmax=""
    desmin = ""

    for compareStocks in comparedata:
        targetlength=len(compareStocks)
        if len(data)<targetlength:
            continue
        datatoday = data.tail(n=targetlength)
        corrcoef.caculateCorrcoefData(datatoday)
        ave_k =corrcoef.caculateCorrcoef(compareStocks,datatoday)
        if ave_k>maxk:
            maxk=ave_k
            desmax = compareStocks.iloc[0]["dynamic_para"]

        if ave_k < mink:
            mink=ave_k
            desmin = compareStocks.iloc[0]["dynamic_para"]

    if maxk > 0.7 or mink <-0.7:
        dynamic_parastr=f"{round(maxk+1, 2)}-{desmax}-{round(mink+1, 2)}-{desmin}"
        return True,dynamic_parastr
    return False
