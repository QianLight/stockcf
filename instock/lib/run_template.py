#!/usr/local/bin/python
# -*- coding: utf-8 -*-


import logging
import datetime
import concurrent.futures
import sys
import time
from tqdm import tqdm
import instock.lib.trade_time as trd

__author__ = 'myh '
__date__ = '2023/3/10 '


# 通用函数，获得日期参数，支持批量作业。
def run_with_args(run_fun, *args):
    if len(sys.argv) == 3:
        # 区间作业 python xxx.py 2023-03-01 2023-03-21
        tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
        start_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
        tmp_year, tmp_month, tmp_day = sys.argv[2].split("-")
        end_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
        run_date = start_date
        day_count=(end_date-run_date)
        #p = tqdm(total=day_count.days, desc="当前执行时间进度:")
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                lastexecutor=None
                while run_date <= end_date:
                    if trd.is_trade_date(run_date):
                        if lastexecutor is None:
                           print(f"执行当前时间: {run_date} 函数:{run_fun.__name__}")
                           lastexecutor=executor.submit(run_fun, run_date, *args)

                        if lastexecutor is not None:
                            if lastexecutor.done():
                                run_date += datetime.timedelta(days=1)
                                #p.update(1)
                                lastexecutor=None
                    else:
                        run_date += datetime.timedelta(days=1)
                        #p.update(1)

                    time.sleep(0.1)


        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")
    elif len(sys.argv) == 2:
        # N个时间作业 python xxx.py 2023-03-01,2023-03-02
        dates = sys.argv[1].split(',')
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for date in dates:
                    tmp_year, tmp_month, tmp_day = date.split("-")
                    run_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
                    if trd.is_trade_date(run_date):
                        executor.submit(run_fun, run_date, *args)
                        time.sleep(2)
        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")
    else:
        # 当前时间作业 python xxx.py
        try:
            run_date, run_date_nph = trd.get_trade_date_last()
            if run_fun.__name__.startswith('save_nph'):
                run_fun(run_date_nph, False)
            else:
                run_fun(run_date, *args)
        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")
