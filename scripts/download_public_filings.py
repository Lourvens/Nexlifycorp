#!/usr/bin/env python3
"""Download public SEC EDGAR filings into data/public via sec-edgar-downloader."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DEFAULT_FORMS, DEFAULT_LIMIT, DEFAULT_TICKERS  # noqa: E402
from paths import PROJECT_ROOT, PUBLIC_DATA_DIR  # noqa: E402
from sec_client import create_downloader, download_with_pause  # noqa: E402


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(PROJECT_ROOT / ".env")


def _sec_identity(
    company_name: str | None,
    email_address: str | None,
) -> tuple[str, str]:
    company = company_name or os.getenv("SEC_EDGAR_COMPANY_NAME")
    email = email_address or os.getenv("SEC_EDGAR_EMAIL")
    if not company or not email:
        print(
            "SEC EDGAR requires a company name and email in the User-Agent.\n"
            "Set SEC_EDGAR_COMPANY_NAME and SEC_EDGAR_EMAIL in .env, or pass "
            "--company-name and --email.",
            file=sys.stderr,
        )
        sys.exit(1)
    return company, email


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download public SEC filings into data/public. "
            "Files are stored under data/public/sec-edgar-filings/."
        ),
    )
    parser.add_argument(
        "--ticker",
        "-t",
        action="append",
        dest="tickers",
        metavar="TICKER",
        help="Ticker to download (repeatable). Defaults to project peer set when omitted.",
    )
    parser.add_argument(
        "--form",
        "-f",
        action="append",
        dest="forms",
        metavar="FORM",
        help="Form type (e.g. 10-K, 10-Q). Repeatable. Default: 10-K and 10-Q.",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=None,
        help=f"Max filings per ticker/form (default: {DEFAULT_LIMIT}).",
    )
    parser.add_argument(
        "--all-available",
        action="store_true",
        help="Download every matching filing (no per ticker/form cap).",
    )
    parser.add_argument(
        "--after",
        help="Only filings on or after YYYY-MM-DD.",
    )
    parser.add_argument(
        "--before",
        help="Only filings on or before YYYY-MM-DD.",
    )
    parser.add_argument(
        "--include-amends",
        action="store_true",
        help="Include amended filings (e.g. 10-K/A).",
    )
    parser.add_argument(
        "--download-details",
        action="store_true",
        help="Also download parseable detail documents (HTML/XML).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PUBLIC_DATA_DIR,
        help=f"Download root directory (default: {PUBLIC_DATA_DIR.relative_to(PROJECT_ROOT)}).",
    )
    parser.add_argument(
        "--company-name",
        help="SEC User-Agent company name (overrides SEC_EDGAR_COMPANY_NAME).",
    )
    parser.add_argument(
        "--email",
        help="SEC User-Agent email (overrides SEC_EDGAR_EMAIL).",
    )
    parser.add_argument(
        "--defaults",
        action="store_true",
        help=(
            "Shortcut for default tickers and forms "
            f"({', '.join(DEFAULT_TICKERS)} / {', '.join(DEFAULT_FORMS)})."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    args = _parse_args(argv)

    tickers = list(args.tickers) if args.tickers else list(DEFAULT_TICKERS)
    forms = list(args.forms) if args.forms else list(DEFAULT_FORMS)

    if args.all_available:
        limit = None
    elif args.limit is not None:
        limit = args.limit
    else:
        limit = DEFAULT_LIMIT

    company, email = _sec_identity(args.company_name, args.email)
    output_dir = args.output_dir.resolve()

    print(f"Saving to: {output_dir}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Forms:   {', '.join(forms)}")
    if limit is not None:
        print(f"Limit:   {limit} per ticker/form")

    downloader = create_downloader(company, email, output_dir)
    total = download_with_pause(
        downloader,
        tickers=tickers,
        forms=forms,
        limit=limit,
        after=args.after,
        before=args.before,
        include_amends=args.include_amends,
        download_details=args.download_details,
    )
    print(f"Done. Downloaded {total} filing(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
