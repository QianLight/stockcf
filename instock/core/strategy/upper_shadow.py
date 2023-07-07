def check(code_name, data, date=None, ma_short=30, ma_long=250, threshold=2):
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

    if data.iloc[-2]['close']<data.iloc[-2]['open']:
        return False

    if data.iloc[-2]['high']<=data.iloc[-2]['close']:
        return False

    deltaChange=data.iloc[-2]['high']-data.iloc[-1]['close']

    ratio= deltaChange / data.iloc[-2]['high']*100
    if ratio<10:
        return False


    return True
