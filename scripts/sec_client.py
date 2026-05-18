"""Resilient SEC EDGAR downloader setup (retries + ticker/CIK cache)."""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from sec_edgar_downloader import Downloader
from sec_edgar_downloader import _Downloader as _downloader_mod
from sec_edgar_downloader import _orchestrator as _orchestrator_mod

from paths import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "data" / "public" / ".cache"
TICKER_CIK_CACHE = CACHE_DIR / "ticker_cik_mapping.json"
CACHE_MAX_AGE = timedelta(days=7)

_RETRYABLE = (
    requests.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
)


def _load_cached_mapping() -> dict[str, str] | None:
    if not TICKER_CIK_CACHE.is_file():
        return None
    try:
        payload = json.loads(TICKER_CIK_CACHE.read_text(encoding="utf-8"))
        fetched_at = datetime.fromisoformat(payload["fetched_at"])
        if datetime.now(UTC) - fetched_at > CACHE_MAX_AGE:
            return None
        mapping = payload.get("mapping")
        if not isinstance(mapping, dict) or not mapping:
            return None
        return {str(k).upper(): str(v) for k, v in mapping.items()}
    except (OSError, ValueError, TypeError, KeyError):
        return None


def _save_cached_mapping(mapping: dict[str, str]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "mapping": mapping,
    }
    TICKER_CIK_CACHE.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _patch_ticker_mapping(mapping: dict[str, str]) -> None:
    def _cached_get_ticker_to_cik_mapping(_user_agent: str) -> dict[str, str]:
        return mapping

    _orchestrator_mod.get_ticker_to_cik_mapping = _cached_get_ticker_to_cik_mapping
    _downloader_mod.get_ticker_to_cik_mapping = _cached_get_ticker_to_cik_mapping


def create_downloader(
    company_name: str,
    email_address: str,
    output_dir: Path,
    *,
    max_retries: int = 5,
    base_delay: float = 2.0,
) -> Downloader:
    """Create a Downloader, using a local ticker/CIK cache when available."""
    output_dir.mkdir(parents=True, exist_ok=True)

    cached = _load_cached_mapping()
    if cached:
        print(f"Using cached ticker/CIK map ({TICKER_CIK_CACHE.relative_to(PROJECT_ROOT)})")
        _patch_ticker_mapping(cached)

    last_error: BaseException | None = None
    for attempt in range(max_retries):
        try:
            downloader = Downloader(company_name, email_address, output_dir)
            if not cached:
                _save_cached_mapping(downloader.ticker_to_cik_mapping)
            return downloader
        except _RETRYABLE as exc:
            last_error = exc
            if attempt >= max_retries - 1:
                break
            delay = base_delay * (2**attempt)
            print(
                f"SEC connection error ({exc!r}), "
                f"retrying in {delay:.0f}s ({attempt + 1}/{max_retries})...",
                file=sys.stderr,
            )
            time.sleep(delay)

    raise RuntimeError(
        "Could not connect to SEC EDGAR after "
        f"{max_retries} attempts. Check your network, wait a few minutes, "
        "and verify SEC_EDGAR_COMPANY_NAME / SEC_EDGAR_EMAIL in .env."
    ) from last_error


def download_with_pause(
    downloader: Downloader,
    *,
    tickers: list[str],
    forms: list[str],
    limit: int | None,
    after: str | None,
    before: str | None,
    include_amends: bool,
    download_details: bool,
    pause_seconds: float = 0.25,
) -> int:
    """Download filings with a short pause between SEC requests."""
    total = 0
    jobs = [(ticker, form) for ticker in tickers for form in forms]
    for index, (ticker, form) in enumerate(jobs):
        count = _get_with_retries(
            downloader,
            form,
            ticker,
            limit=limit,
            after=after,
            before=before,
            include_amends=include_amends,
            download_details=download_details,
        )
        print(f"  {ticker} {form}: {count} filing(s)")
        total += count
        if pause_seconds and index < len(jobs) - 1:
            time.sleep(pause_seconds)
    return total


def _get_with_retries(
    downloader: Downloader,
    form: str,
    ticker: str,
    **kwargs: Any,
) -> int:
    max_retries = 4
    base_delay = 2.0
    last_error: BaseException | None = None

    for attempt in range(max_retries):
        try:
            return downloader.get(form, ticker, **kwargs)
        except _RETRYABLE as exc:
            last_error = exc
            if attempt >= max_retries - 1:
                break
            delay = base_delay * (2**attempt)
            print(
                f"  {ticker} {form}: connection error, retrying in {delay:.0f}s...",
                file=sys.stderr,
            )
            time.sleep(delay)

    raise RuntimeError(f"Failed to download {ticker} {form} from SEC EDGAR.") from last_error
