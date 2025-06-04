import argparse
import pandas as pd

import run_scheduler
from analysis import MarketAnalysis


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("expiry", type=str, help="Expiry code (e.g. '23MAY25')")
    parser.add_argument("t1", type=int, help="Total runtime in seconds")
    parser.add_argument("t2", type=int, help="Interval in seconds between computations")
    parser.add_argument("strikes", nargs='+', type=float, help="List of strike prices (space-separated)")
    return parser.parse_args()


def export_results(results, filename='results.csv'):
    rows = [
        {'timestamp': timestamp, 'strike': strike, **data}
        for timestamp, strikes in results.items()
        for strike, data in strikes.items()
    ]
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8-sig')


def main():
    args = parse_args()
    analysis = MarketAnalysis(args.expiry, args.strikes)
    run_scheduler.do_runs(analysis, args.t1, args.t2)
    export_results(analysis.results)


if __name__ == "__main__":
    main()
