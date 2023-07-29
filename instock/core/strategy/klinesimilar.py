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

    dynamic_parastr=""

    for compareStocks in comparedata:
        targetlength=len(compareStocks)
        if len(data)<targetlength:
            continue
        datatoday = data.tail(n=targetlength)
        corrcoef.caculateCorrcoefData(datatoday)
        ave_k =corrcoef.caculateCorrcoef(compareStocks,datatoday)
        desmax = compareStocks.iloc[0]["dynamic_para"]

        if ave_k>=compareStocks.iloc[0]["maxvalue"]:
           dynamic_parastr += f"正{round(ave_k, 2)}-{desmax}-"

        if ave_k<=compareStocks.iloc[0]["minvalue"]:
           dynamic_parastr += f"负{round(ave_k, 2)}-{desmin}-"


    if len(dynamic_parastr)>0:
        return True,dynamic_parastr
    return False
