import time


def do_runs(obj_to_run, runtime, interval):
    start_time = time.time()
    while time.time() < start_time + runtime:
        time.sleep(interval)
        obj_to_run.run()
