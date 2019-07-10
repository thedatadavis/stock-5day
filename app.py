from flask import Flask, request, jsonify
import requests

import utils.forecast as fc
import utils.data_loader as dl

from multiprocessing import Process


app = Flask(__name__)

dow30 = [
    'MMM', 'AXP', 'AAPL', 'BA', 'CAT',
    'CVX', 'CSCO', 'KO', 'DOW', 'XOM',
    'GS', 'HD', 'IBM', 'INTC', 'JNJ',
    'JPM', 'MCD', 'MRK', 'MSFT', 'NKE',
    'PFE', 'PG', 'TRV', 'UNH', 'UTX',
    'VZ', 'V', 'WMT', 'WBA', 'DIS',
]

def ping_bubble(ticker, version):
    url = 'https://stock-5day.bubbleapps.io/version-{}/api/1.1/wf/update_forecast?'.format(version)
    r = requests.post(url + 'ticker={}'.format(ticker))
    print('updating', ticker, '- status', r.status_code)
    return ticker

def data_loader(ticker, version):
    url = 'https://stock-5day.bubbleapps.io/version-{}/api/1.1/wf/add_dow30?'.format(version)
    r = requests.post(url + 'ticker={}&stock={}'.format(ticker[0], ticker[1]))
    return 'done'

# -------------------------- ROUTES -----------------------------------------------

@app.route('/')
def home():
    return 'STOCK 5DAY'

@app.route('/version')
def get_version():
    version = {'yes': 'test', 'no': 'live'}
    is_dev = request.args.get('is_dev')
    return version[is_dev]

@app.route('/split_text', methods=['GET'])
def split_text():

    stock_full = request.args.get('stock')
    stock_split = stock_full.split(' - ')

    ticker = stock_split[0]
    company = stock_split[1]

    return jsonify({'ticker': ticker, 'company': company})

@app.route('/get_forecast', methods=['GET'])
def get_data():
    ticker = request.args.get('ticker')
    version = request.args.get('version', 'test') # test or live
    print('trying for', ticker)
    forecast = fc.forecast_stock(ticker, version)

    return jsonify(forecast)

@app.route('/update_trigger')
def trigger():
    version = request.args.get('version', 'test')
    
    procs = []

    # instantiating process with arguments
    for ticker in dow30:
        proc = Process(target=ping_bubble, args=(ticker, version))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()
        
    return 'done'

@app.route('/add_dow30')
def add_tickers_to_db():
    version = request.args.get('version', 'test')
    
    procs = []
    dow30 = dl.stock_list()
    for ticker in dow30:
        proc = Process(target=data_loader, args=(ticker, version))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()
    return 'done'
