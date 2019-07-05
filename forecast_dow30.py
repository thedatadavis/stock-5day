import pandas as pd
import requests
import json
import os
from datetime import datetime

from fbprophet import Prophet

dow30 = [
    'MMM', 'AXP', 'AAPL', 'BA', 'CAT',
    'CVX', 'CSCO', 'KO', 'DOW', 'XOM',
    'GS', 'HD', 'IBM', 'INTC', 'JNJ',
    'JPM', 'MCD', 'MRK', 'MSFT', 'NKE',
    'PFE', 'PG', 'TRV', 'UNH', 'UTX',
    'VZ', 'V', 'WMT', 'WBA', 'DIS',
]

def get_stock_data(ticker):
    token = os.getenv('STOCK_PRICE_API_TOKEN')
    sb = 'https://sandbox.iexapis.com/stable/stock/{}/chart/1m?token={}'.format(ticker, token)
    r = requests.get(sb)

    print('\nSTATUS {} - '.format(r.status_code),
            '...pinging IEX for {}'.format(ticker))

    res_json = json.dumps(r.json())
    df = pd.read_json(res_json, orient='records')
    df.rename(columns={'date':'ds'}, inplace=True)

    df_open_pred = forecast_stock_price(df, 'open')
    df_close_pred = forecast_stock_price(df, 'close')

    df_pred = pd.concat([df_open_pred, df_close_pred], axis=1)
    df_pred = df_pred.loc[:,~df_pred.columns.duplicated()] #drop dup columns

    df_pred['day_pred'] = [ 'up' if row['close_pred']-row['open_pred'] >= 0 \
                            else 'down' for i, row in df_pred.iterrows() ]


    df_forecasts = df_pred[df_pred['ds'] >= datetime.today() ].head()
    
    fc_result = {
        'ticker' : ticker,
        'forecasts': df_forecasts.to_dict(orient='records')
        }

    print('5-day forecast generated for {}'.format(ticker.upper()))
    return( fc_result )

def forecast_stock_price(dframe, col):
    df_calc = dframe.copy(deep=True)
    df_calc = df_calc[['ds', col]]

    df_calc.rename(columns={col:'y'}, inplace=True)

    m_calc = Prophet(changepoint_prior_scale=0.0677)
    m_calc.fit(df_calc)

    future_calc = m_calc.make_future_dataframe(periods=10)

    forecast_calc = m_calc.predict(future_calc)
    res = forecast_calc[['ds', 'yhat']].tail(10)
    res = res[res['yhat'] > 0]
    res.rename(columns={'yhat': col + '_pred'}, inplace=True)
    
    return res

if __name__ == "__main__":
    get_stock_data('AAPL')
