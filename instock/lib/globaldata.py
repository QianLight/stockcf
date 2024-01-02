import logging
import concurrent.futures

import numpy as np
import pandas as pd
import os.path
import sys
import datetime
import talib as tl

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
#import instock.core.tablestructure as tbs
import instock.core.stockfetch as stf

BASIC_DATA_DAILYDATA=[]

BenchMarkData=[]
def GetBenchMark():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    code="510300"

    global BenchMarkData
    if len(BenchMarkData) == 0:
        BenchMarkData = stf.fetch_etf_hist((date, code))

    return BenchMarkData

def caculatekdj(data):

    if 'kdjj' in data.columns:
        return

    # kdjk
    data.loc[:, 'kdjk'], data.loc[:, 'kdjd'] = tl.STOCH(
        data['high'].values, data['low'].values, data['close'].values, fastk_period=9,
        slowk_period=5, slowk_matype=1, slowd_period=5, slowd_matype=1)
    data['kdjk'].values[np.isnan(data['kdjk'].values)] = 0.0
    data['kdjd'].values[np.isnan(data['kdjd'].values)] = 0.0
    data.loc[:, 'kdjj'] = 3 * data['kdjk'].values - 2 * data['kdjd'].values



if __name__ == '__main__':
    data=GetBenchMark()


