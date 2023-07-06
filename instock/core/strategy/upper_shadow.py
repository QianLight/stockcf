def check(code_name, data, date=None, ma_short=30, ma_long=250, threshold=1):
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

    if data['close'].values<data['open'].values:
        return False

    if data['high'].values<=data['close'].values:
        return False

    deltaChange=data['high']-data['close']

    ratio= deltaChange / data['high']*100
    if ratio.values[0]>=4:
        return True

    return False
