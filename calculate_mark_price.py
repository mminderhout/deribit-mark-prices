import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from datetime import datetime, timezone


def fit_iv_curve(data, func, trim_outer_strikes=7, trim_high_iv=1.8):
    x_points = np.tile(data['strike'].values, 2)
    # x_points = np.concatenate([x_points, x_points])
    y_points = data[['bid_iv', 'ask_iv']].values.flatten()

    mask = (y_points != 0) & (y_points < np.mean(y_points) * trim_high_iv)
    x_trim = x_points[mask][trim_outer_strikes:-trim_outer_strikes]
    y_trim = y_points[mask][trim_outer_strikes:-trim_outer_strikes]

    params, covariance = curve_fit(func, x_trim, y_trim)
    return params


def get_time_to_expiry(expiry_code):
    day = int(expiry_code[:2])
    month_str = expiry_code[2:5].upper()
    year = int(expiry_code[5:]) + 2000

    date_str = f"{day} {month_str} {year} 08:00"
    expiry = datetime.strptime(date_str, "%d %b %Y %H:%M").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    delta_years = (expiry - now).total_seconds() / (365.25 * 24 * 3600)
    return delta_years


def bs_option_price(iv, tau, S, r, K):
    d1 = 1/(iv * np.sqrt(tau)) * (np.log(S/K) + (r + (iv**2 / 2)) * tau)
    d2 = d1 - iv * np.sqrt(tau)
    call = norm.cdf(d1) * S - norm.cdf(d2) * K * np.exp(-r * tau)
    put = norm.cdf(-d2) * K * np.exp(-r * tau) - norm.cdf(-d1) * S
    return call, put


def run(expiry, strikes, market, strikes_available):
    data = market.get_current_prices()
    data_df = pd.DataFrame.from_dict(data, orient="index")
    data_df['strike'] = np.repeat(strikes_available, 2)

    def func(x, a, b, c, d):
        return a + b * x + c * x**2 + d * x**3
    iv_params = fit_iv_curve(data_df, func)
    my_iv = func(np.asarray(strikes), *iv_params)
    tau = get_time_to_expiry(expiry)
    S = np.mean(data_df['underlying'])
    r = np.mean(data_df['interest_rate'])

    results = {}
    for strike, iv in zip(strikes, my_iv):
        call, put = bs_option_price(iv/100, tau, S, r, strike)
        results[strike] = {
            'C': call/S,
            'P': put/S,
            'C_ref': data_df[data_df.index.str.endswith(str(strike)[:-2] + '-C')]['mark'].item() if strike in strikes_available else None,
            'P_ref': data_df[data_df.index.str.endswith(str(strike)[:-2] + '-P')]['mark'].item() if strike in strikes_available else None,
            'timestamp': np.median(data_df['timestamp'])
        }
        if strike in strikes_available:
            results[strike]['C_diff'] = str((results[strike]['C'] / results[strike]['C_ref'] - 1) * 100)[:5] + '%'
            results[strike]['P_diff'] = str((results[strike]['P'] / results[strike]['P_ref'] - 1) * 100)[:5] + '%'

    return results



