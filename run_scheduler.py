import time
from datetime import datetime, timezone

from market_data import Deribit
import analysis


def do_runs(runtime, interval, expiry, strikes):
    strikes_available = get_available_strikes(expiry)
    market = Deribit(expiry, strikes_available)
    market.start()

    results = {}

    start_time = time.time()
    while time.time() < start_time + runtime:
        time.sleep(interval)
        current_results = calculate_mark_price.run(expiry, strikes, market, strikes_available)
        timestamp = datetime.fromtimestamp(current_results[strikes[0]]['timestamp'] / 1000, tz=timezone.utc).isoformat()
        results[timestamp] = current_results

    return results
