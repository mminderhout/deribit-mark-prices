import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# def split_calls_puts_dataframes(data):
#     calls = {}
#     puts = {}
#
#     for instrument, data in data.items():
#         if instrument.endswith("C"):
#             calls[instrument] = data
#         elif instrument.endswith("P"):
#             puts[instrument] = data
#
#     calls_df = pd.DataFrame.from_dict(calls, orient="index")
#     puts_df = pd.DataFrame.from_dict(puts, orient="index")
#
#     return calls_df, puts_df


def fit_iv_curve(data, func, trim_outer_strikes=7, trim_high_iv=1.8):
    x_points = np.tile(data['strike'].values, 2)
    # x_points = np.concatenate([x_points, x_points])
    y_points = data[['bid_iv', 'ask_iv']].values.flatten()

    mask = (y_points != 0) & (y_points < np.mean(y_points) * trim_high_iv)
    x_trim = x_points[mask][trim_outer_strikes:-trim_outer_strikes]
    y_trim = y_points[mask][trim_outer_strikes:-trim_outer_strikes]

    params, covariance = curve_fit(func, x_trim, y_trim)

    #TODO: remove plotting
    plt.scatter(x_trim, func(x_trim, *params), color='red')
    plt.scatter(x_trim, y_trim, color='blue')
    plt.savefig('fitted values in red 3.png')
    plt.close()

    return params


def run(expiry, strikes, market, strikes_available):
    # TODO: get data from market_data DONE
    #  fit iv curve DONE
    #  use black scholes to calculate mark prices for given strikes
    #  send these to data_out together with their timestamp

    data = market.get_current_prices()

    # calls, puts = split_calls_puts_dataframes(data)
    # calls['strike'] = strikes_available
    # puts['strike'] = strikes_available

    data_df = pd.DataFrame.from_dict(data, orient="index")
    data_df['strike'] = np.repeat(strikes_available, 2)

    def func(x, a, b, c, d):
        return a + b * x + c * x**2 + d * x**3
    iv_params = fit_iv_curve(data_df, func)

    my_iv = func(np.asarray(strikes), *iv_params)



    # call_iv_params = fit_iv_curve(calls, func)
    # put_iv_params = fit_iv_curve(puts, func)
    #
    # my_calls_iv = func(np.asarray(strikes), *call_iv_params)
    # my_puts_iv = func(np.asarray(strikes), *call_iv_params)


