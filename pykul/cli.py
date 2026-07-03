#!/usr/bin/env python3
"""CLI runner for .http files. Kulala-style, Termux-friendly.

Usage:
    pykul requests.http -l                 # list requests
    pykul requests.http -i 2                # run request #2
    pykul requests.http -n "create user"    # run by name (partial match)
    pykul requests.http --line 42           # run the request containing line 42 (editor integration)
    pykul requests.http                     # runs automatically if file has only 1 request
    pykul requests.http --verbose           # show all response headers, not just the important ones
"""
import argparse
import sys

from . import __version__
from .parser import parse_file, find_request_at_line
from .runner import execute
from .formatter import pretty_print


def main():
    ap = argparse.ArgumentParser(prog="pykul", description="A lightweight, Kulala-inspired HTTP client for the terminal")
    ap.add_argument("file", help="Path to .http file")
    ap.add_argument("-l", "--list", action="store_true", help="List all requests in the file")
    ap.add_argument("-n", "--name", help="Run request by name (partial match)")
    ap.add_argument("-i", "--index", type=int, help="Run request by index (1-based)")
    ap.add_argument("--line", type=int, help="Run the request nearest to this line number (for editor integration)")
    ap.add_argument("--verbose", action="store_true", help="Print all response headers instead of just the important ones")
    ap.add_argument("--version", action="version", version=f"pykul {__version__}")
    ap.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="Copy the response body to the clipboard",
    )

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
            print(f"{i}. {req.name}  [{req.method} {req.url}]  (line {req.line})")
        return

    target = None
    if args.line is not None:
        target = find_request_at_line(requests_list, args.line)
        if target is None:
            print(f"No request found at or before line {args.line}.")
            sys.exit(1)
    elif args.index:
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
            print("Multiple requests found. Use -l to list, then -n NAME, -i INDEX, or --line N to run one.")
            for i, req in enumerate(requests_list, 1):
                print(f"{i}. {req.name}")
            sys.exit(1)

    try:
        response, elapsed = execute(target)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    pretty_print(response, elapsed, target, verbose=args.verbose, copy=args.copy)


if __name__ == "__main__":
    main()


