"""Defaults for public SEC filing downloads (Nexlify KB learning corpus)."""

# SaaS / enterprise software peers used as real public comparables for Nexlify Corp.
DEFAULT_TICKERS: tuple[str, ...] = ("CRM", "NOW", "WDAY", "DDOG", "ZS", "NVDA")

# Core periodic reports for financial RAG experiments.
DEFAULT_FORMS: tuple[str, ...] = ("10-K", "10-Q")

# Recent filings per ticker/form pair (keeps initial download size reasonable).
DEFAULT_LIMIT = 2
