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

    if len(data)>=threshold:
       data = data.tail(n=threshold)
       data.reset_index(inplace=True, drop=True)

    daymin = data.iloc[-1]['low']

    maxallTime=data['high'].values.max()
    daymin_max_ratio = round((maxallTime - daymin) / maxallTime,2)
    max_index = data['high'].idxmax()+1
    daymin_max_ratio_day=len(data)-max_index

    minallTime = data['low'].values.min()
    daymin_low_ratio =  round((daymin - minallTime) / daymin,2)
    low_index = data['low'].idxmin()+1
    daymin_low_ratio_day = len(data) - low_index

    #if data.iloc[-1]['open']<data.iloc[-1]['low']:
    #   return False

    #if data.iloc[-1]['quote_change']>9.8:
    #    return False

    amplitude=round(data.iloc[-1]['amplitude'], 2)
    p_change=round(data.iloc[-1]['p_change'], 2)

    if p_change<0:
        amplitude=-amplitude

    #if data.iloc[-1]['quote_change']>5 and data.iloc[-1]['amplitude']>5:

    desshow=f"{amplitude}:{p_change}," \
            f"{daymin_max_ratio_day}:{daymin_max_ratio},{daymin_low_ratio_day}:{daymin_low_ratio}"
    if abs(amplitude) > 5:
        return True,desshow

    return False
