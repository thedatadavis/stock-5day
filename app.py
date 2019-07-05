from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/split_text', methods=['GET'])
def split_text():

    stock_full = request.args.get('stock')
    stock_split = stock_full.split(' - ')

    ticker = stock_split[0]
    company = stock_split[1]

    return jsonify({'ticker': ticker, 'company': company})
