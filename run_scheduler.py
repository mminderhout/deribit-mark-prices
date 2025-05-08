import time

import calculate_mark_price

def start(runtime, interval, expiry, strikes):
    start_time = time.time()
    while time.time() < start_time + runtime:
        time.sleep(interval)
        calculate_mark_price.run(expiry, strikes)
