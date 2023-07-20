import logging
import concurrent.futures

import numpy as np
import pandas as pd
import os.path
import sys
import datetime

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.core.backtest.rate_stats as rate
import instock.core.tablestructure as tablestructure
from instock.core.singleton_stock import stock_hist_data
from tqdm import tqdm

def CaculateEarnRatio(data, keyword,tagDes):
    mask = (data[keyword] >0)
    mask_neg=data[keyword] <0
    data_neg = data.loc[mask_neg].copy()
    data_earn = data.loc[mask].copy()
    if len(data_earn)+len(data_neg)==0:
       return

    data_earn_ratio=len(data_earn)/(len(data_earn)+len(data_neg))
    #if data_earn_ratio>0.8:
    print(f"{tagDes} {keyword} ratio:{data_earn_ratio} {len(data)} {len(data_earn)} {len(data_neg)}");


def main():
    table_name ="cn_stock_strategy_increaselarge"
    table_name = "cn_stock_indicators_buy"
    now_date = datetime.datetime.now().date()
    sql = f"SELECT * FROM `{table_name}` WHERE `date` < '{now_date}'"
    data = pd.read_sql(sql=sql, con=mdb.engine())
    data=data.drop_duplicates(subset=["code"], keep="first", inplace = False, ignore_index = False)
    dataRate = data.iloc[:, 4:]
    data.insert(1, "last_site", data.ffill(axis=1).iloc[:, -1])

    #minvalueIndexLabel = data.idxmin()

    allDataFramesByCode = data.groupby('date')

    #CaculateEarnRatio(data, f"rate_1", "total")

    for i in range(1, tablestructure.RATE_FIELDS_COUNT + 1, 1):
        CaculateEarnRatio(data, f"rate_{i}", "total")
    #    for date, group in allDataFramesByCode:
    #        CaculateEarnRatio(group, f"rate_{i}", date)


    #for date, group in allDataFramesByCode:
    #    CaculateEarnRatio(group,"rate_1",date)

    print("finish!");


# main函数入口
if __name__ == '__main__':
    main()
