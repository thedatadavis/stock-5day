from flask import Flask, request, jsonify
import forecast_dow30 as fc
import requests

app = Flask(__name__)

dow30 = [
    'MMM', 'AXP', 'AAPL', 'BA', 'CAT',
    'CVX', 'CSCO', 'KO', 'DOW', 'XOM',
    'GS', 'HD', 'IBM', 'INTC', 'JNJ',
    'JPM', 'MCD', 'MRK', 'MSFT', 'NKE',
    'PFE', 'PG', 'TRV', 'UNH', 'UTX',
    'VZ', 'V', 'WMT', 'WBA', 'DIS',
]

@app.route('/')
def home():
    return 'STOCK 5DAY'

@app.route('/split_text', methods=['GET'])
def split_text():

    stock_full = request.args.get('stock')
    stock_split = stock_full.split(' - ')

    ticker = stock_split[0]
    company = stock_split[1]

    return jsonify({'ticker': ticker, 'company': company})

@app.route('/get_data', methods=['GET'])
def get_data():
    ticker = request.args.get('ticker')
    print('trying for', ticker)
    forecast = fc.get_stock_data(ticker)

    return jsonify(forecast)

@app.route('/update_trigger')
def trigger():
    
    counter = 0
    for ticker in dow30:
        url = 'https://stock-5day.bubbleapps.io/version-test/api/1.1/wf/update_forecast?'
        r = requests.post(url + 'ticker={}'.format(ticker))
        if r.status_code == 200:
            counter += 1

    print(counter, 'of 30 added to test')
    return 'done'

@app.route('/add_dow30_to_test')
def add_dow30_test():

    counter = 0
    for ticker in dow30:
        url = 'https://stock-5day.bubbleapps.io/version-test/api/1.1/wf/add_dow30?'
        r = requests.post(url + 'ticker={}'.format(ticker))
        if r.status_code == 200:
            counter += 1

    print(counter, 'of 30 added to test')
    return 'done'

@app.route('/add_dow30_to_prod')
def add_dow30_prod():

    counter = 0
    for ticker in dow30:
        url = 'https://stock-5day.bubbleapps.io/version-live/api/1.1/wf/add_dow30?'
        r = requests.post(url + 'ticker={}'.format(ticker))
        if r.status_code == 200:
            counter += 1

    print(counter, 'of 30 added to prod')
    return 'done'
