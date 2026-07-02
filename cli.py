#!/usr/bin/env python3
"""CLI runner for .http files. Kulala-style, Termux-friendly.

Usage:
    python3 cli.py requests.http -l                # list requests
    python3 cli.py requests.http -i 2               # run request #2
    python3 cli.py requests.http -n "create user"   # run by name (partial match)
    python3 cli.py requests.http                    # run if file has only 1 request
"""
import argparse
import sys

from parser import parse_file
from runner import execute
from formatter import pretty_print


def main():
    ap = argparse.ArgumentParser(description="Simple .http request runner")
    ap.add_argument("file", help="Path to .http file")
    ap.add_argument("-l", "--list", action="store_true", help="List all requests in the file")
    ap.add_argument("-n", "--name", help="Run request by name (partial match)")
    ap.add_argument("-i", "--index", type=int, help="Run request by index (1-based)")
    ap.add_argument("--verbose", action="store_true", help="Print all response headers instead of just the important ones")

    args = ap.parse_args()

    try:
        requests_list, _ = parse_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    if not requests_list:
        print("No requests found in file.")
        sys.exit(1)

    if args.list:
        for i, req in enumerate(requests_list, 1):
            print(f"{i}. {req.name}  [{req.method} {req.url}]")
        return

    target = None
    if args.index:
        if 1 <= args.index <= len(requests_list):
            target = requests_list[args.index - 1]
        else:
            print(f"Index out of range. File has {len(requests_list)} requests.")
            sys.exit(1)
    elif args.name:
        matches = [r for r in requests_list if args.name.lower() in r.name.lower()]
        if not matches:
            print(f"No request matched name: {args.name}")
            sys.exit(1)
        target = matches[0]
    else:
        if len(requests_list) == 1:
            target = requests_list[0]
        else:
            print("Multiple requests found. Use -l to list, then -n NAME or -i INDEX to run one.")
            for i, req in enumerate(requests_list, 1):
                print(f"{i}. {req.name}")
            sys.exit(1)

    try:
        response, elapsed = execute(target)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    pretty_print(response, elapsed, target, verbose=args.verbose)


if __name__ == "__main__":
    main()

