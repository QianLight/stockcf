import schedule

def fun(name, age):
    print("我是一个定时器", name, age)

schedule.every(5).seconds.do(fun, "李明", 12)  # 每隔5s运行一次

while True:
    schedule.run_pending()  # 运行所有可以运行的任务