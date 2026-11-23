"""Offline examples of password brute force and password spraying."""

import argparse
import sys
from collections.abc import Iterable, Mapping
from typing import Optional


def brute_force(
    passwords: Iterable[str],
    secret: str,
) -> Optional[str]:
    """Return the first candidate equal to ``secret``, or ``None``."""
    for candidate in passwords:
        if candidate == secret:
            return candidate
    return None


def password_spray(
    accounts: Mapping[str, str],
    password: str,
) -> list[str]:
    """Return usernames whose account password equals ``password``."""
    return [
        username
        for username, account_password in accounts.items()
        if account_password == password
    ]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline password brute-force and spraying demonstrations"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    brute = subparsers.add_parser("brute-force")
    brute.add_argument("--target", required=True, help="Password to find")
    brute.add_argument(
        "--passwords",
        nargs="+",
        required=True,
        help="Candidate passwords, in testing order",
    )

    spray = subparsers.add_parser("spray")
    spray.add_argument("--password", required=True, help="Password to spray")
    spray.add_argument(
        "--accounts",
        nargs="+",
        action="append",
        required=True,
        metavar=("USERNAME", "PASSWORD"),
        help="Username and password pairs",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.mode == "brute-force":
        match = brute_force(args.passwords, args.target)
        if match is None:
            print("No match")
            return 1
        print("Match found")
        return 0

    accounts = {}
    for pair in args.accounts:
        if len(pair) != 2:
            print("Each account must contain exactly two values: USERNAME PASSWORD")
            return 2
        username, password = pair
        accounts[username] = password

    matches = password_spray(accounts, args.password)
    if matches:
        print("{} match(es) found".format(len(matches)))
        return 0

    print("No matches")
    return 1


if __name__ == "__main__":
    sys.exit(main())
