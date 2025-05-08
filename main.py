import argparse
import pandas as pd

import run_scheduler


def parse_args():
    parser = argparse.ArgumentParser(description="Deribit Mark Price Calculator")
    parser.add_argument("expiry", type=str, help="Expiry code (e.g. '23MAY25')")
    parser.add_argument("t1", type=int, help="Total runtime in seconds")
    parser.add_argument("t2", type=int, help="Interval in seconds between computations")
    parser.add_argument("strikes", nargs='+', type=float, help="List of strike prices (space-separated)")
    return parser.parse_args()


def export_results(dict, filename='results.csv'):
    rows = []
    for timestamp, strikes in dict.items():
        for strike, metrics in strikes.items():
            row = {'timestamp': timestamp, 'strike': strike}
            row.update(metrics)  # Add 'mark', 'iv', etc.
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8-sig')


def main():
    args = parse_args()
    results = run_scheduler.start(args.t1, args.t2, args.expiry, args.strikes)
    export_results(results)


if __name__ == "__main__":
    main()
