from instock.lib import globaldata
def check(code_name, data, date=None, ma_short=30, ma_long=7, threshold=60):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < ma_long:
        return False

    data = data.tail(n=2)

    lastClose=data.iloc[-2]['close']

    # if data.iloc[-1]['open']>lastClose and data.iloc[-1]['close']>lastClose:
    #     return True

    if data.iloc[-1]['open']<lastClose and data.iloc[-1]['close']<lastClose:
        return True

    return False
