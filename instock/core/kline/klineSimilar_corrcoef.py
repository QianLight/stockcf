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

    allScore=[]
    allScore.append(np.corrcoef(leftdata['open'], rightdata['open'])[0][1])
    allScore.append(np.corrcoef(leftdata['close'], rightdata['close'])[0][1])
    allScore.append( np.corrcoef(leftdata['high'], rightdata['high'])[0][1])
    allScore.append(np.corrcoef(leftdata['low'], rightdata['low'])[0][1])
    allScore.append(np.corrcoef(leftdata['volume'], rightdata['volume'])[0][1])
    allScore.append(np.corrcoef(leftdata['turnover'], rightdata['turnover'])[0][1])
    allScore.append(np.corrcoef(leftdata['amplitude'], rightdata['amplitude'])[0][1])
    allScore.append(np.corrcoef(leftdata['p_change'], rightdata['p_change'])[0][1])
    #allScore.append(np.corrcoef(leftdata['ma5'], rightdata['ma5'])[0][1])
    #allScore.append(np.corrcoef(leftdata['fromhigh'], rightdata['fromhigh'])[0][1])
    #allScore.append(np.corrcoef(leftdata['fromlow'], rightdata['fromlow'])[0][1])
    ave_k = sum(allScore)/len(allScore)
    return ave_k