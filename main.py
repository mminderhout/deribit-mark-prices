import argparse
import sys

import data_out
import run_scheduler
from market_data import Deribit

#TODO: remove this line before final commit
sys.argv = ['main.py', '23MAY25', '20', '5', '98000', '99000']

def parse_args():
    parser = argparse.ArgumentParser(description="Deribit Mark Price Calculator")
    parser.add_argument("expiry", type=str, help="Expiry code (e.g. '23MAY25')")
    parser.add_argument("t1", type=int, help="Total runtime in seconds")
    parser.add_argument("t2", type=int, help="Interval in seconds between computations")
    parser.add_argument("strikes", nargs='+', type=float, help="List of strike prices (space-separated)")
    return parser.parse_args()


def main():
    args = parse_args()
    results = data_out.OutputStorage()
    run_scheduler.start(args.t1, args.t2, args.expiry, args.strikes)


if __name__ == "__main__":
    main()
