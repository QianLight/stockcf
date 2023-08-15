def check(code_name, data, date=None, threshold=2):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < threshold:
        return False

    open1=data.iloc[-1]['open']
    open2 = data.iloc[-2]['close']
    ratio=(open1-open2)/open2*100
    if ratio>0:
        return True,round(ratio,3)

    return False