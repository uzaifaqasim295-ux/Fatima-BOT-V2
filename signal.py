from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import random
import time

app = Flask(__name__)
CORS(app)

def calculate_rsi(prices, period=14):
    if len(prices) < period: return 50
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.route('/get-signal')
def get_signal():
    pair = request.args.get('pair', 'EURUSD=X')
    if "_OTC" in pair:
        time.sleep(1)
        res = random.choice(["UP (CALL)", "DOWN (PUT)"])
        return jsonify({"pair": pair.replace("_", "/"), "direction": res, "time": "OTC Mode Active"})
    else:
        try:
            data = yf.download(pair, period='1d', interval='1m', progress=False)
            if data.empty: return jsonify({"pair": pair, "direction": "MARKET CLOSED", "time": "Try OTC"})
            close_prices = data['Close'].tolist()
            rsi_val = calculate_rsi(close_prices)
            sig = "DOWN (PUT)" if rsi_val > 60 else "UP (CALL)" if rsi_val < 40 else "WAIT"
            return jsonify({"pair": pair.replace("=X", ""), "direction": sig, "time": f"RSI: {round(rsi_val, 2)}"})
        except:
            return jsonify({"pair": "Error", "direction": "RETRY", "time": "Network Error"})

if __name__ == '__main__':
    print("FATIMA ALGO BOT v2 IS NOW LIVE!")
    app.run(port=5000)