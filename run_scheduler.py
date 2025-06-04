import time
from datetime import datetime, timezone

from market_data import Deribit
import analysis


def do_runs(obj_to_run, runtime, interval):
    start_time = time.time()
    while time.time() < start_time + runtime:
        time.sleep(interval)
        obj_to_run.run()

        # current_results = calculate_mark_price.run(expiry, strikes, market, strikes_available)
        # timestamp = datetime.fromtimestamp(current_results[strikes[0]]['timestamp'] / 1000, tz=timezone.utc).isoformat()
        # results[timestamp] = current_results

    # return results
