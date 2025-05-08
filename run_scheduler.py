import time
import requests

from market_data import Deribit
import calculate_mark_price


def get_available_strikes(expiry_code, currency='BTC'):
    url = "https://www.deribit.com/api/v2/public/get_instruments"
    params = {"currency": currency, "kind": "option"}
    response = requests.get(url, params=params)
    data = response.json()

    strikes = set()

    for instrument in data["result"]:
        if instrument["expiration_timestamp"] and expiry_code in instrument["instrument_name"]:
            strikes.add(instrument["strike"])

    return sorted(strikes)

def start(runtime, interval, expiry, strikes):
    strikes_available = get_available_strikes(expiry)
    market = Deribit(expiry, strikes_available)
    market.start()

    start_time = time.time()
    while time.time() < start_time + runtime:
        time.sleep(interval)
        calculate_mark_price.run(expiry, strikes, market, strikes_available)
