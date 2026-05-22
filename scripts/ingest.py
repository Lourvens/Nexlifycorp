#!/usr/bin/env python3
"""
NexlifyCorp Ingestion CLI

Examples:
    # SEC filings
    uv run python scripts/ingest.py sec NVDA
    uv run python scripts/ingest.py sec NVDA --year 2024
    uv run python scripts/ingest.py sec AAPL --form 10-Q

    # Internal documents (doc_type: board_memo, risk_register, product_roadmap, etc.)
    uv run python scripts/ingest.py internal TEST-001 board_memo -f doc.md
    uv run python scripts/ingest.py internal TEST-001 risk_register -c "## Risk\n\nContent"

    # Management
    uv run python scripts/ingest.py stats
    uv run python scripts/ingest.py list
    uv run python scripts/ingest.py clear --confirm
"""
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import VectorStore
from src.ingestion import create_ingestion_pipeline
from src.utils.logger import logger


# =============================================================================
# SEC Commands
# =============================================================================

@click.group()
def cli():
    """NexlifyCorp document ingestion CLI."""
    pass


SEC_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py sec NVDA
  uv run python scripts/ingest.py sec NVDA --year 2024
  uv run python scripts/ingest.py sec AAPL --form 10-Q
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=SEC_EXAMPLES)
@click.argument("ticker")
@click.option("--year", type=int, help="Fiscal year (default: latest)")
@click.option("--form", type=click.Choice(["10-K", "10-Q"]), default="10-K", help="10-K or 10-Q")
def sec(ticker: str, year: int | None, form: str):
    """Ingest SEC filing."""
    pipeline = create_ingestion_pipeline()
    ticker = ticker.upper()

    logger.info(f"Ingesting {ticker} {form} ({year or 'latest'})...")

    try:
        count = pipeline.ingest_sec_filing(
            ticker=ticker,
            year=year,
            form=form,
        )

        if count > 0:
            click.echo(f"✓ Ingested {count} chunks for {ticker} {form}")
        else:
            click.echo(f"✗ No chunks generated for {ticker} {form}", err=True)
            raise SystemExit(1)

    except Exception as e:
        logger.error(f"Failed to ingest {ticker}: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        raise SystemExit(1)


# =============================================================================
# Internal Document Commands
# =============================================================================

INTERNAL_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py internal TEST-001 board_memo -f doc.md
  uv run python scripts/ingest.py internal TEST-001 risk_register -c "## Risk\n\nContent"
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=INTERNAL_EXAMPLES)
@click.argument("doc_id")
@click.argument("doc_type")
@click.option("--file", "-f", type=click.Path(exists=True), help="Markdown file path")
@click.option("--content", "-c", help="Inline markdown content")
def internal(doc_id: str, doc_type: str, file: str | None, content: str | None):
    """Ingest internal document."""
    # Validate input source
    if file:
        content = Path(file).read_text(encoding="utf-8")
    elif content:
        pass  # Use content as-is
    else:
        click.echo("✗ Error: Must provide --file/-f or --content/-c", err=True)
        raise SystemExit(1)

    pipeline = create_ingestion_pipeline()
    logger.info(f"Ingesting internal doc {doc_id} ({doc_type})...")

    try:
        count = pipeline.ingest_internal_doc(
            doc_id=doc_id,
            doc_type=doc_type,
            content=content,
        )

        if count > 0:
            click.echo(f"✓ Ingested {count} chunks for internal doc {doc_id}")
        else:
            click.echo(f"✗ No chunks generated for internal doc {doc_id}", err=True)
            raise SystemExit(1)

    except Exception as e:
        logger.error(f"Failed to ingest internal doc: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        raise SystemExit(1)


# =============================================================================
# Stats Command
# =============================================================================

STATS_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py stats
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=STATS_EXAMPLES)
def stats():
    """Show vector store stats."""
    vs = VectorStore()

    click.echo(f"Collection: {vs.collection_name}")
    click.echo(f"Documents:  {vs.count}")
    click.echo(f"URL:        {vs.url}")

    # Show breakdown by source
    try:
        all_docs = vs.get_all(limit=10000)
        public_count = sum(1 for d in all_docs if d.metadata.get("is_public", False))
        internal_count = len(all_docs) - public_count

        click.echo(f"\nBy access level:")
        click.echo(f"  Public:    {public_count}")
        click.echo(f"  Internal:  {internal_count}")

    except Exception as e:
        logger.debug(f"Could not get breakdown: {e}")


# =============================================================================
# List Command
# =============================================================================

LIST_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py list
  uv run python scripts/ingest.py list --limit 500
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=LIST_EXAMPLES)
@click.option("--limit", type=int, default=1000, help="Max documents to list")
def list(limit: int):
    """List all documents."""
    vs = VectorStore()

    if not vs.exists():
        click.echo("Collection does not exist yet.")
        return

    all_docs = vs.get_all(limit=limit)

    if not all_docs:
        click.echo("No documents in vector store.")
        return

    click.echo(f"Documents in vector store ({len(all_docs)} total):\n")

    # Group by source_detail
    by_source: dict[str, list] = {}
    for doc in all_docs:
        source = doc.metadata.get("source_detail", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(doc)

    for source, docs in sorted(by_source.items()):
        is_public = docs[0].metadata.get("is_public", False)
        access = "PUBLIC" if is_public else "INTERNAL"
        click.echo(f"  [{access}] {source} ({len(docs)} chunks)")


# =============================================================================
# Clear Command
# =============================================================================

CLEAR_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py clear --confirm
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=CLEAR_EXAMPLES)
@click.option("--confirm", is_flag=True, help="Confirm clearing the vector store")
def clear(confirm: bool):
    """Clear all documents from the vector store."""
    if not confirm:
        vs = VectorStore()
        click.echo("To clear, use: ingest.py clear --confirm")
        click.echo(f"Current count: {vs.count} documents")
        raise SystemExit(1)

    vs = VectorStore()
    count = vs.count
    vs.clear()
    click.echo(f"✓ Cleared {count} documents from vector store")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    cli()