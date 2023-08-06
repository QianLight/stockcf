from flask import Flask, redirect, url_for, request, g
import instock.core.crawling.stock_hist_em as she
import instock.job.klineSimilar_corrcoef_job as ks
import instock.job.showstocks_job as showstocks
import datetime
import pandas as pd
import json

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

def getdata(name):
   return 'welcome %s' % name


@app.route('/histdata',methods = ['POST'])
def histdata():
    stock= Gethistdata()
    return stock.to_json(orient="split",force_ascii=False)


def Gethistdata():
    code = request.form['code']
    period = request.form['period']
    date_start = request.form['date_start']
    date_end = request.form['date_end']
    adjust = request.form['adjust']

    if period == "1d":
        stock = she.stock_zh_a_hist(symbol=code, period="daily", start_date=date_start, end_date=date_end,
                                    adjust=adjust)
    else:
        stock = she.stock_zh_a_hist_min_em(symbol=code, period=period, start_date=date_start, end_date=date_end,
                                           adjust=adjust)
    return stock


last_dfData=[]

@app.route('/stock_zh_a_spot_em',methods = ['POST'])
def stock_zh_a_spot_em():
      stockFilterName = request.form['stockFilterName']
      stockFilterCode = request.form['stockFilterCode']

      dfData = she.stock_zh_a_spot_em()
      if len(stockFilterName)!=0:
          dfData=dfData.drop(dfData[(dfData['名称'].str.startswith(stockFilterName)==False)].index)
      if len(stockFilterCode) != 0:
          dfData=dfData.drop(dfData[(dfData['代码'].str.startswith(stockFilterCode)==False)].index)

      global last_dfData
      last_dfData=dfData

      dfJson = dfData.to_json(orient="split", force_ascii=False)
      return dfJson


@app.route('/klineSimilar_corrcoef_job',methods = ['POST'])
def klineSimilar_corrcoef_job():
      code=request.form['code']
      klineStartTime = request.form['klineStartTime']
      klineEndTime = request.form['klineEndTime']
      period = request.form['period']
      date_start = request.form['date_start']
      date_end = request.form['date_end']
      adjust = request.form['adjust']

      stock = Gethistdata()
      stock["ma5"] = ks.MA(stock["收盘"], 5)

      stock["日期"] = pd.to_datetime(stock["日期"])
      mask = stock["日期"] >= klineStartTime
      stock = stock.loc[mask]
      mask = stock["日期"] <= klineEndTime
      stock = stock.loc[mask]

      data=ks.prepare(stock, datetime.datetime.strptime(date_end, '%Y%m%d').date())
      return data.to_json(orient="split", force_ascii=False)

@app.route('/showstocks_job',methods = ['POST'])
def showstocks_job():
      data=showstocks.main()
      json_data = json.dumps(data,ensure_ascii=False)
      return json_data



if __name__ == '__main__':
   app.run(host="192.168.0.109", debug = True, use_reloader=False)
