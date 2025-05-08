import json
from websocket import WebSocketApp
import threading
import time

class Deribit:
    def __init__(self, expiry, strikes, currency='BTC'):
        self.ws = None
        self.expiry_code = expiry
        self.strikes = strikes
        self.currency = currency
        self.instrument_data = {}

    def on_message(self, ws, message):
        now = time.time()
        data = json.loads(message)
        if 'params' in data and 'data' in data['params']:
            instrument = data['params']['channel'].split('.')[1]
            tick = data['params']['data']
            self.instrument_data[instrument] = {
                'bid': tick.get('best_bid_price'),
                'ask': tick.get('best_ask_price'),
                'bid_iv': tick.get('bid_iv'),
                'ask_iv': tick.get('ask_iv'),
                'mark': tick.get('mark_price'),
                'underlying': tick.get('underlying_price'),
                'timestamp': now,
            }
    def on_open(self, ws):
        print("WebSocket Connected.")
        for strike in self.strikes:
            for opt_type in ["C", "P"]:
                instrument = f"{self.currency}-{self.expiry_code}-{int(strike)}-{opt_type}"
                channel = f"ticker.{instrument}.100ms"
                sub_msg = {
                    "jsonrpc": "2.0",
                    "method": "public/subscribe",
                    "id": 16,
                    "params": {"channels": [channel]}
                }
                ws.send(json.dumps(sub_msg))

#TODO: remove on_error and on_close later
    def on_error(self, ws, error):
        print(f"WebSocket Error {error}")
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket Connection closed")

    def start(self):
        def run():
            self.ws = WebSocketApp(
                "wss://www.deribit.com/ws/api/v2",
                on_message=self.on_message,
                on_open=self.on_open,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.run_forever()
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    def get_current_prices(self):
        return self.instrument_data.copy()