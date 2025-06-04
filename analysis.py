import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import norm
from datetime import datetime, timezone
import requests

from market_data import Deribit


class MarketAnalysis:
    def __init__(self, expiry_code, strikes, currency='BTC'):
        self.expiry_code = expiry_code
        self.strikes = strikes
        self.currency = currency
        self.available_strikes = self.get_available_strikes()
        self.market = Deribit(self.expiry_code, self.available_strikes)
        self.market.start()
        self.results = {}


    def get_time_to_expiry(self):
        expiry_code = self.market.expiry_code

        day = int(expiry_code[:2])
        month = expiry_code[2:5].upper()
        year = int(expiry_code[5:]) + 2000

        date_str = f"{day} {month} {year} 08:00"
        expiry = datetime.strptime(date_str, "%d %b %Y %H:%M").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        return (expiry - now).total_seconds() / (365.25 * 24 * 60 * 60)


    def get_available_strikes(self):
        url = "https://www.deribit.com/api/v2/public/get_instruments"
        params = {
            "currency": self.currency,
            "kind": "option"
        }
        response = requests.get(url, params=params)
        data = response.json()
        strikes = set()
        for instrument in data["result"]:
            if instrument["expiration_timestamp"] and self.expiry_code in instrument["instrument_name"]:
                strikes.add(instrument["strike"])
        return sorted(strikes)


    @staticmethod
    def bs_option_price(iv, tau, S, r, K):
        d1 = 1/(iv * np.sqrt(tau)) * (np.log(S/K) + (r + (iv**2 / 2)) * tau)
        d2 = d1 - iv * np.sqrt(tau)
        call = norm.cdf(d1) * S - norm.cdf(d2) * K * np.exp(-r * tau)
        put = norm.cdf(-d2) * K * np.exp(-r * tau) - norm.cdf(-d1) * S
        return call, put

    @staticmethod
    def fit_iv_curve(data, fitfunc, trim_outer_strikes=7, trim_high_iv=1.8):
        x_points = np.tile(data['strike'].values, 2)
        y_points = data[['bid_iv', 'ask_iv']].values.flatten()

        mask = (y_points != 0) & (y_points < np.mean(y_points) * trim_high_iv)
        x_trim = x_points[mask][trim_outer_strikes:-trim_outer_strikes]
        y_trim = y_points[mask][trim_outer_strikes:-trim_outer_strikes]

        params, covariance = curve_fit(fitfunc, x_trim, y_trim)
        return params

    @staticmethod
    def fitfunc(x, a, b, c, d):
        return a + b * x + c * x**2 + d * x**3


    def run(self):
        data = self.market.get_current_market_data()
        data_df = pd.DataFrame.from_dict(data, orient="index")
        data_df['strike'] = np.repeat(self.available_strikes, 2)

        iv_params = self.fit_iv_curve(data_df, self.fitfunc)
        my_iv = self.fitfunc(np.asarray(self.strikes), *iv_params)
        tau = self.get_time_to_expiry()
        S = np.mean(data_df['underlying'])
        r = np.mean(data_df['interest_rate'])

        results = {}
        for strike, iv in zip(self.strikes, my_iv):
            call, put = self.bs_option_price(iv/100, tau, S, r, strike)
            results[strike] = {
                'C': call/S,
                'P': put/S,
                'C_ref': data_df[data_df.index.str.endswith(str(strike)[:-2] + '-C')]['mark'].item() if strike in self.available_strikes else None,
                'P_ref': data_df[data_df.index.str.endswith(str(strike)[:-2] + '-P')]['mark'].item() if strike in self.available_strikes else None,
                'timestamp': np.median(data_df['timestamp'])
            }
            if strike in self.available_strikes:
                results[strike]['C_diff'] = str((results[strike]['C'] / results[strike]['C_ref'] - 1) * 100)[:5] + '%'
                results[strike]['P_diff'] = str((results[strike]['P'] / results[strike]['P_ref'] - 1) * 100)[:5] + '%'

        timestamp = datetime.fromtimestamp(results[self.strikes[0]]['timestamp'] / 1000, tz=timezone.utc).isoformat()
        self.results[timestamp] = results



