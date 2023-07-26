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

    open_k = np.corrcoef(compareStocks['open'], data['open'])[0][1]
    # /**-------------计算相关系数-------------------*/
    close_k = np.corrcoef(compareStocks['close'], compareStocks['close'])[0][1]
    high_k = np.corrcoef(compareStocks['high'], compareStocks['high'])[0][1]
    low_k = np.corrcoef(compareStocks['low'], compareStocks['low'])[0][1]
    # ma5_k = np.corrcoef(compare_ma5, ma5_o)[0][1]
    ave_k = (open_k + close_k + high_k + low_k) / 4
    if ave_k > 0.95:
        return True
    return False