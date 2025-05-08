import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def split_calls_puts_dataframes(data):
    calls = {}
    puts = {}

    for instrument, data in data.items():
        if instrument.endswith("C"):
            calls[instrument] = data
        elif instrument.endswith("P"):
            puts[instrument] = data

    calls_df = pd.DataFrame.from_dict(calls, orient="index")
    puts_df = pd.DataFrame.from_dict(puts, orient="index")

    return calls_df, puts_df


def fit_iv_curve(data):
    x_points = data['strike'].values
    x_points = np.concatenate([x_points, x_points])
    y_points = data[['bid_iv', 'ask_iv']].values.flatten()

    mask = y_points != 0
    x_clean = x_points[mask]
    y_clean = y_points[mask]

    def func(x, a, b, c):
        return a + b * x + c * x * x



def run(expiry, strikes, market, strikes_available):
    # get data from market_data
    # fit iv curve
    # use black scholes to calculate mark prices
    # send these to data_out together with their timestamp
    data = market.get_current_prices()
    calls, puts = split_calls_puts_dataframes(data)
    calls['strike'] = strikes_available
    puts['strike'] = strikes_available

    call_iv_curve = fit_iv_curve(calls)
    put_iv_curve = fit_iv_curve(puts)



