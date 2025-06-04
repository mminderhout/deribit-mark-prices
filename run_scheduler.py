import time


def do_runs(obj_to_run, runtime, interval):
    run_moments = [time.time() + interval * i for i in range(int(runtime/interval))]
    run_number = 0
    last_run = len(run_moments) - 1
    while True:
        if time.time() > run_moments[run_number]:
            obj_to_run.run()
            if run_number == last_run:
                break
            else:
                run_number += 1
        else:
            time.sleep(0.5)