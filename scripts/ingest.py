#!/usr/bin/env python3
"""
NexlifyCorp Ingestion CLI

Examples:
    # Public filings (SEC EDGAR)
    uv run python scripts/ingest.py public NVDA
    uv run python scripts/ingest.py public NVDA --year 2024
    uv run python scripts/ingest.py public AAPL --form 10-Q

    # Internal documents (doc_type: board_memo, risk_register, product_roadmap, etc.)
    uv run python scripts/ingest.py internal TEST-001 board_memo -f doc.md
    uv run python scripts/ingest.py internal TEST-001 risk_register -c "## Risk\n\nContent"

    # Auto-ingest
    uv run python scripts/ingest.py auto
    uv run python scripts/ingest.py auto --type sec
    uv run python scripts/ingest.py auto --type internal

    # Management
    uv run python scripts/ingest.py stats
    uv run python scripts/ingest.py list
    uv run python scripts/ingest.py manifest
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
# Public Document Commands (SEC EDGAR)
# =============================================================================

@click.group()
def cli():
    """NexlifyCorp document ingestion CLI."""
    pass


PUBLIC_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py public NVDA
  uv run python scripts/ingest.py public NVDA --year 2024
  uv run python scripts/ingest.py public AAPL --form 10-Q
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=PUBLIC_EXAMPLES)
@click.argument("ticker")
@click.option("--year", type=int, help="Fiscal year (default: latest)")
@click.option("--form", type=click.Choice(["10-K", "10-Q"]), default="10-K", help="10-K or 10-Q")
def public(ticker: str, year: int | None, form: str):
    """Ingest public filing (SEC EDGAR)."""
    pipeline = create_ingestion_pipeline()
    ticker = ticker.upper()

    logger.info(f"[cyan]Ingesting[/cyan] {ticker} [cyan]{form}[cyan] ([yellow]{year or 'latest'}[yellow])...")

    try:
        count = pipeline.ingest_sec_filing(
            ticker=ticker,
            year=year,
            form=form,
        )

        if count > 0:
            logger.info(f"[green]✓[/green] Ingested [bold]{count}[/bold] chunks for [cyan]{ticker} {form}[cyan]")
        else:
            logger.warning(f"[yellow]✗[/yellow] No chunks generated for [cyan]{ticker} {form}[cyan]")
            raise SystemExit(1)

    except Exception as e:
        logger.error(f"[red]✗[/red] Failed to ingest [cyan]{ticker}[cyan]: {e}")
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
        logger.error("[red]✗[/red] Must provide [cyan]--file/-f[/cyan] or [cyan]--content/-c[/cyan]")
        raise SystemExit(1)

    pipeline = create_ingestion_pipeline()
    logger.info(f"[cyan]Ingesting[/cyan] internal doc [yellow]{doc_id}[yellow] ([cyan]{doc_type}[cyan])...")

    try:
        count = pipeline.ingest_internal_doc(
            doc_id=doc_id,
            doc_type=doc_type,
            content=content,
        )

        if count > 0:
            logger.info(f"[green]✓[/green] Ingested [bold]{count}[/bold] chunks for internal doc [yellow]{doc_id}[yellow]")
        else:
            logger.warning(f"[yellow]✗[/yellow] No chunks generated for internal doc [yellow]{doc_id}[yellow]")
            raise SystemExit(1)

    except Exception as e:
        logger.error(f"[red]✗[/red] Failed to ingest internal doc: {e}")
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

    logger.info(f"[bold]Vector Store Stats[/bold]")
    logger.info(f"  Collection: [cyan]{vs.collection_name}[cyan]")
    logger.info(f"  Documents:  [bold]{vs.count}[/bold]")
    logger.info(f"  URL:        [dim]{vs.url}[dim]")

    # Show breakdown by source
    try:
        all_docs = vs.get_all(limit=10000)
        public_count = sum(1 for d in all_docs if d.metadata.get("is_public", False))
        internal_count = len(all_docs) - public_count

        click.echo(f"\nBy access level:")
        logger.info(f"  [green]Public[/green]:    [bold]{public_count}[/bold]")
        logger.info(f"  [yellow]Internal[/yellow]:  [bold]{internal_count}[/bold]")

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
        logger.warning("[yellow]Collection does not exist yet.[/yellow]")
        return

    all_docs = vs.get_all(limit=limit)

    if not all_docs:
        logger.info("[cyan]No documents in vector store.[/cyan]")
        return

    logger.info(f"[bold]Documents in vector store[/bold] ([bold]{len(all_docs)}[/bold] total):\n")

    # Group by source_detail
    by_source: dict[str, list] = {}
    for doc in all_docs:
        source = doc.metadata.get("source_detail", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(doc)

    for source, docs in sorted(by_source.items()):
        is_public = docs[0].metadata.get("is_public", False)
        access_color = "green" if is_public else "yellow"
        access_label = "PUBLIC" if is_public else "INTERNAL"
        logger.info(f"  [{access_color}]{access_label}[/{access_color}] {source} ([bold]{len(docs)}[/bold] chunks)")


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
        logger.warning("[yellow]To clear, use:[/yellow] [cyan]ingest.py clear --confirm[/cyan]")
        logger.info(f"Current count: [bold]{vs.count}[/bold] documents")
        raise SystemExit(1)

    vs = VectorStore()
    count = vs.count
    vs.clear()
    logger.info(f"[green]✓[/green] Cleared [bold]{count}[/bold] documents from vector store")


# =============================================================================
# Auto Commands
# =============================================================================

AUTO_PUBLIC_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py auto-public
  uv run python scripts/ingest.py auto-public --tickers NVDA,AAPL,MSFT
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=AUTO_PUBLIC_EXAMPLES)
@click.option("--tickers", help="Comma-separated tickers (default: config tickers)")
def auto_public(tickers: str | None):
    """Auto-ingest all new public filings (SEC EDGAR) from configured tickers."""
    from src.ingestion.manifest import get_manifest

    manifest = get_manifest()
    pipeline = create_ingestion_pipeline()

    # Get tickers from param or config
    if tickers:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
    else:
        from scripts.config import DEFAULT_TICKERS
        ticker_list = [*DEFAULT_TICKERS]

    logger.info(f"[bold]Auto-ingesting public filings[/bold] ({len(ticker_list)} tickers)")

    total = 0
    for ticker in ticker_list:
        count = pipeline.ingest_sec_filing(ticker=ticker, year=None, form="10-K")
        if count > 0:
            total += count

    if total > 0:
        logger.info(f"[green]✓[/green] Auto-public complete: [bold]{total}[/bold] chunks added")
    else:
        logger.info("[cyan]No new public filings to ingest[/cyan]")


AUTO_INTERNAL_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py auto-internal
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=AUTO_INTERNAL_EXAMPLES)
def auto_internal():
    """Auto-ingest all new internal documents."""
    from src.ingestion.manifest import get_manifest
    from src.ingestion.internal_doc_processor import extract_all_internal_documents

    manifest = get_manifest()
    pipeline = create_ingestion_pipeline()

    # Get internal docs directory from config
    from src.core.config import get_settings
    settings = get_settings()
    internal_dir = settings.internal_docs_dir

    logger.info(f"[bold]Auto-ingesting internal documents[/bold] from {internal_dir}")

    total = 0
    # Process all markdown files in internal directory
    for folder in internal_dir.iterdir():
        if not folder.is_dir():
            continue

        doc_type = folder.name.replace("-", "_")
        for md_file in folder.glob("*.md"):
            doc_id = md_file.stem
            if manifest.is_ingested(doc_id):
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                count = pipeline.ingest_internal_doc(
                    doc_id=doc_id,
                    doc_type=doc_type,
                    content=content,
                )
                if count > 0:
                    total += count
            except Exception as e:
                logger.warning(f"[yellow]Skipped {doc_id}: {e}[/yellow]")

    if total > 0:
        logger.info(f"[green]✓[/green] Auto-internal complete: [bold]{total}[/bold] chunks added")
    else:
        logger.info("[cyan]No new internal docs to ingest[/cyan]")


AUTO_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py auto
  uv run python scripts/ingest.py auto --type public
  uv run python scripts/ingest.py auto --type internal
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=AUTO_EXAMPLES)
@click.option("--type", "auto_type", type=click.Choice(["public", "internal", "all"]), default="all", help="Type to ingest")
@click.pass_context
def auto(ctx: click.Context, auto_type: str):
    """Auto-ingest all new documents (public + internal)."""
    if auto_type in ("public", "all"):
        ctx.invoke(auto_public)
    if auto_type in ("internal", "all"):
        ctx.invoke(auto_internal)


RESET_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py reset NVDA_10K_2024
  uv run python scripts/ingest.py reset TEST-001
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=RESET_EXAMPLES)
@click.argument("doc_id")
def reset(doc_id: str):
    """Remove document from manifest (allows re-ingest)."""
    from src.ingestion.manifest import get_manifest

    manifest = get_manifest()

    if manifest.remove(doc_id):
        logger.info(f"[green]✓[/green] Removed [cyan]{doc_id}[cyan] from manifest")
    else:
        logger.warning(f"[yellow]Document not in manifest:[/yellow] [cyan]{doc_id}[cyan]")


MANIFEST_EXAMPLES = """
Examples:
  uv run python scripts/ingest.py manifest
  uv run python scripts/ingest.py manifest --type sec
"""


@cli.command(context_settings=dict(ignore_unknown_options=True), epilog=MANIFEST_EXAMPLES)
@click.option("--type", "filter_type", type=click.Choice(["sec", "internal"]), default=None, help="Filter by type")
def manifest(filter_type: str | None):
    """Show ingestion manifest."""
    from src.ingestion.manifest import get_manifest

    manifest = get_manifest()

    if manifest.count == 0:
        logger.info("[cyan]Manifest is empty[/cyan]")
        return

    logger.info(f"[bold]Ingestion Manifest[/bold] ([bold]{manifest.count}[/bold] documents):")

    for doc_id, info in manifest.list_all():
        if filter_type and info.get("type") != filter_type:
            continue

        doc_type = info.get("type", "unknown")
        type_color = "green" if doc_type == "sec" else "yellow"
        chunks = info.get("chunks", "?")
        ingested_at = info.get("ingested_at", "unknown")

        logger.info(f"  [{type_color}]{doc_type}[/{type_color}] [cyan]{doc_id}[cyan] ({chunks} chunks)")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    cli()