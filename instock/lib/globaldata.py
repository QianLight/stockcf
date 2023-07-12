import logging
import concurrent.futures
import pandas as pd
import os.path
import sys
import datetime

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.core.tablestructure as tbs
import instock.core.stockfetch as stf


BenchMarkData=[]
def GetBenchMark():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    code="510500"

    global BenchMarkData
    if len(BenchMarkData) == 0:
        BenchMarkData = stf.fetch_etf_hist((date, code))

    return BenchMarkData


if __name__ == '__main__':
    data=GetBenchMark()


