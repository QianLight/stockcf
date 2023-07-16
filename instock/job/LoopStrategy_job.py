# -*- coding:utf-8 -*-
import threading
import time

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import datetime
import concurrent.futures
import logging
import os.path
import sys

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
log_path = os.path.join(cpath_current, 'log')
if not os.path.exists(log_path):
    os.makedirs(log_path)
logging.basicConfig(format='%(asctime)s %(message)s', filename=os.path.join(log_path, 'stock_execute_job.log'))
logging.getLogger().setLevel(logging.INFO)
import init_job as bj
import self_basic_data_daily_job as hdj
import basic_data_other_daily_job as hdtj
import indicators_data_daily_job as gdj
#import self_strategy_data_daily_job as sdj
#import self_backtest_data_daily_job as bdj
import strategy_data_daily_job as sdj
import backtest_data_daily_job as bdj
import klinepattern_data_daily_job as kdj

__author__ = 'myh '
__date__ = '2023/3/10 '


def LoopStrategy():
    start = time.time()
    _start = datetime.datetime.now()
    print("######## 任务执行时间: %s #######" % _start.strftime("%Y-%m-%d %H:%M:%S.%f"))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(sdj.main)

    # # # # 第6步创建股票回测
    bdj.main()

    print("######## 完成任务, 使用时间: %s 秒 #######" % (time.time() - start))
    #LoopStrategy()

#def LoopStrategy():
#	# 打印当前时间
#    print(time.strftime('%Y-%m-%d %H:%M:%S'))
#    #threading.Timer(3, heart_beat).start()

if __name__ == '__main__':
    LoopStrategy()
    #heart_beat()
    # 15秒后停止定时器
    #time.sleep(15)
    #cancel_tmr = True
