import logging
import pandas as pd
import numpy as np
import talib as tl

def MA(S,N):              #求序列的N日简单移动平均值，返回序列
    return pd.Series(S).rolling(N).mean().values

def get_klineSimilar(headstock_key,compareStocks,code_name,data,date=None, threshold=60):

    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)
    caculateCorrcoefData(data)
    ave_k =caculateCorrcoef(compareStocks,data)
    if ave_k > 0.95:
        return True
    return False
def caculatema5(data):
    if 'ma5' in data.columns:
        return

    data["ma5"] = MA(data["close"], 5)

def caculateCorrcoefData(data):
    maxvalue = data["high"].max()
    minvalue = data["low"].min()
    data["fromhigh"] = (maxvalue - data["low"]) / maxvalue
    data["fromlow"] = (data["low"] - minvalue) / minvalue



def caculateCorrcoef(leftdata,rightdata):
    open_k = np.corrcoef(leftdata['open'], rightdata['open'])[0][1]
    close_k = np.corrcoef(leftdata['close'], rightdata['close'])[0][1]
    high_k = np.corrcoef(leftdata['high'], rightdata['high'])[0][1]
    low_k = np.corrcoef(leftdata['low'], rightdata['low'])[0][1]
    ma5_k = np.corrcoef(leftdata['ma5'], rightdata['ma5'])[0][1]
    fromhigh = np.corrcoef(leftdata['fromhigh'], rightdata['fromhigh'])[0][1]
    fromlow = np.corrcoef(leftdata['fromlow'], rightdata['fromlow'])[0][1]
    ave_k = (open_k + close_k + high_k + low_k + ma5_k + fromhigh + fromlow) / 7
    return ave_k