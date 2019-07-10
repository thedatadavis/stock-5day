import pandas as pd
import requests
import json
import datetime

from .date_calcs import date_by_adding_business_days

def forecast_stock(ticker, version='test'):
    """
    Pings IEX API with stock symbol to pull last month of trade data
    
    Calc procedure:
    1. Request result json => dataframe
    2. Add column for day of week (DOW) index (0 = Monday)
    3. Generate list of next trading days
    4. Calculate daily percent change by (DOW)
    5. Make list of most recent date for each DOW
    6. Loop through most recent list to calculate forecast by DOW
    7. Return data
    
    Returns: Dict
    -------------
    date - a datetime object representing a future trading day
    open_f - forecast for day's open
    close_f - forecast for day's close
    high_f - forecast for day's high
    low_f - forecast for day's low
    day_result_f - forecast for day's performance
    
    """
        
    if version == 'test':
        token = 'Tpk_ebe2d6a630a611e9958142010a80043c'
        url = 'https://sandbox.iexapis.com/stable/stock/{}/chart/1m?token={}'.format(ticker, token)
        
    if version == 'prod':
        token = 'pk_d8f06c2fcddd4e03a4c1bc1d4c4be045'
        url = 'https://cloud.iexapis.com/stable/stock/{}/chart/1m?token={}'.format(ticker, token)

    r = requests.get(url)
    
    df = pd.DataFrame(r.json())
    df['day_of_week'] = [ datetime.datetime.strptime(row['date'], '%Y-%m-%d').weekday() \
                         for i, row in df.iterrows() ]

    # Get next 5 dates

    last_day = datetime.datetime.strptime(df.tail(1)['date'].item(), '%Y-%m-%d')
    future_dates = []

    for x in range(5):
        dt = date_by_adding_business_days(last_day, x+1)
        dow = dt.weekday()

        future_dates.append({'date': dt, 'day_of_week': dow})

    # multiply last_day by average change

    average_daily_change = df.groupby('day_of_week')['changePercent'].mean().to_dict()
    recent_dates = [ df[df['date'] == x] for x in df.groupby('day_of_week')['date'].agg('max') ]

    forecasts = []

    for i, day in enumerate(recent_dates):
        forecast = {
            'date_f': future_dates[i]['date'],
            'open_f': round(day['open'].item() * (1 + (average_daily_change[i]/100)), 2),
            'close_f': round(day['close'].item() * (1 + (average_daily_change[i]/100)), 2),
            'low_f': round(day['low'].item() * (1 + (average_daily_change[i]/100)), 2),
            'high_f': round(day['high'].item() * (1 + (average_daily_change[i]/100)), 2),
        }

        if forecast['close_f'] > forecast['open_f']:
            forecast['day_result_f'] = 'up'
        else:
            forecast['day_result_f'] = 'down'
        forecasts.append(forecast)
        
    return forecasts