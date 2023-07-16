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

    data = data.tail(n=1)

    if data.iloc[-1]['open']<data.iloc[-1]['low']:
        return False

    #if data.iloc[-1]['quote_change']>5 and data.iloc[-1]['amplitude']>5:
    if data.iloc[-1]['amplitude'] > 5:
        return True

    return False
