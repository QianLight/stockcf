def check(code_name, data, date=None, ma_short=30, ma_long=60, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < ma_long:
        return False

    data = data.tail(n=threshold)
    data3 = data.tail(n=3)

    ratio =data3["turnover"].values/data.iloc[-4]['turnover']
    #ration3=ratio.mean()
    if ratio[-3]>4 or ratio[-2]>4:
        return True
    return False




    lastClose= data.iloc[-1]['close']
    low = data['low'].values.min()
    high=data['high'].values.max()
    deltaChange=high-lastClose
    ratio= deltaChange /high*100
    if ratio<30:
        return False

    deltaChange=lastClose-low
    ratio= deltaChange /low*100
    if ratio>5:
        return False

    return True

    deltaChange=data.iloc[-3]['high']-data.iloc[-5]['close']

    ratio = deltaChange / data.iloc[-5]['close'] * 100

    if ratio>10:
        return False

    #if data.iloc[-2]['close']<data.iloc[-2]['open']:
    #    return False

    if data.iloc[-2]['high']<=data.iloc[-2]['close']:
        return False

    deltaChange=data.iloc[-2]['high']-data.iloc[-1]['close']

    ratio= deltaChange / data.iloc[-2]['high']*100
    if ratio<9:
        return False


    return True
