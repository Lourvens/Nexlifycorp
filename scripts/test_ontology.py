#!/usr/bin/env python3
"""
Ontology Enrichment CLI — test and manage ontology metadata in chunks.

Examples:
    # Show ontology metadata for a specific document
    uv run python scripts/test_ontology.py --doc-id NVDA_10K_2024 --show

    # Re-enrich (replace) ontology metadata for a document
    uv run python scripts/test_ontology.py --doc-id NVDA_10K_2024 --re-enrich

    # Enrich new chunks that were ingested without ontology
    uv run python scripts/test_ontology.py --doc-id NVDA_10K_2024 --enrich

    # Full re-enrichment of all chunks in the store
    uv run python scripts/test_ontology.py --all --re-enrich

    # Show stats about ontology enrichment status
    uv run python scripts/test_ontology.py --stats
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
from src.ingestion.ontology_enricher import OntologyEnrichmentStep, OntologySchema
from src.utils.logger import logger


@click.group()
def cli():
    """Ontology enrichment CLI — test and manage ontology metadata in chunks."""
    pass


@cli.command()
@click.option("--doc-id", help="Document ID to show ontology for")
@click.option("--show", "action", flag_value="show", default=True, help="Show ontology metadata (default)")
def show(doc_id: str | None, action: str):
    """Show ontology metadata for a document."""
    vs = VectorStore()

    if not doc_id:
        logger.error("[red]--doc-id required[/red]")
        raise SystemExit(1)

    # Find chunks by document_id
    docs = vs.get_by_document_id(doc_id)

    if not docs:
        logger.warning(f"[yellow]No chunks found for doc_id:[/yellow] [cyan]{doc_id}[cyan]")
        raise SystemExit(1)

    logger.info(f"[bold]Ontology metadata for[/bold] [cyan]{doc_id}[cyan] ([bold]{len(docs)}[/bold] chunks):\n")

    for i, doc in enumerate(docs):
        meta = doc.metadata
        concepts = meta.get("concepts", "") or ""
        themes = meta.get("strategic_themes", "") or ""
        departments = meta.get("departments", "") or ""
        failed = meta.get("ontology_enrichment_failed", False)

        logger.info(f"  [bold]Chunk {i + 1}[/bold] ({meta.get('chunk_id', 'unknown')})")
        logger.info(f"    Concepts:         [cyan]{concepts or '(empty)'}[/cyan]")
        logger.info(f"    Strategic themes: [cyan]{themes or '(empty)'}[/cyan]")
        logger.info(f"    Departments:      [cyan]{departments or '(empty)'}[/cyan]")
        logger.info(f"    Failed:           [red]{failed}[/red]")
        logger.info("")


@cli.command()
@click.option("--doc-id", help="Document ID to re-enrich")
@click.option("--re-enrich", "action", flag_value="re-enrich", help="Replace existing ontology metadata")
@click.option("--enrich", "action", flag_value="enrich", help="Add ontology metadata (skip if already enriched)")
def enrich(doc_id: str | None, action: str):
    """Re-enrich or enrich ontology metadata for a document."""
    vs = VectorStore()
    step = OntologyEnrichmentStep()

    if not doc_id:
        logger.error("[red]--doc-id required[/red]")
        raise SystemExit(1)

    docs = vs.get_by_document_id(doc_id)

    if not docs:
        logger.warning(f"[yellow]No chunks found for doc_id:[/yellow] [cyan]{doc_id}[cyan]")
        raise SystemExit(1)

    logger.info(f"[bold]{'Re-enriching' if action == 're-enrich' else 'Enriching'}[/bold] [cyan]{doc_id}[cyan] ([bold]{len(docs)}[/bold] chunks)...")

    for i, doc in enumerate(docs):
        meta = doc.metadata
        chunk_id = meta.get("chunk_id")

        # Skip if already enriched (for --enrich only)
        if action == "enrich":
            existing = meta.get("concepts") or meta.get("strategic_themes") or meta.get("departments")
            if existing:
                logger.debug(f"  Skipping chunk {i + 1} (already has ontology)")
                continue

        try:
            result = step._get_chain().invoke({"content": doc.page_content[:4000]})
            new_meta = {
                "concepts": ",".join(result.concepts) if result.concepts else "",
                "strategic_themes": ",".join(result.strategic_themes) if result.strategic_themes else "",
                "departments": ",".join(result.departments) if result.departments else "",
                "ontology_enrichment_failed": False,
            }
            vs.update_chunk_metadata(chunk_id, new_meta)
            logger.debug(f"  [green]✓[/green] Chunk {i + 1}: {result.concepts[:3]}")
        except Exception as e:
            logger.warning(f"  [red]✗[/red] Chunk {i + 1} failed: {e}")

    logger.info(f"[green]✓[/green] Done — use [cyan]--show --doc-id {doc_id}[/cyan] to verify")


@cli.command()
@click.option("--re-enrich", "action", flag_value="re-enrich", default=True, help="Re-enrich all chunks")
def all_re_enrich(action: str):
    """Re-enrich all chunks in the vector store."""
    vs = VectorStore()
    step = OntologyEnrichmentStep()

    all_docs = vs.get_all(limit=100000)

    if not all_docs:
        logger.warning("[yellow]No documents in vector store[/yellow]")
        return

    logger.info(f"[bold]Re-enriching all[/bold] [cyan]{len(all_docs)}[/cyan] chunks...")

    for i, doc in enumerate(all_docs):
        meta = doc.metadata
        chunk_id = meta.get("chunk_id")

        try:
            result = step._get_chain().invoke({"content": doc.page_content[:4000]})
            new_meta = {
                "concepts": ",".join(result.concepts) if result.concepts else "",
                "strategic_themes": ",".join(result.strategic_themes) if result.strategic_themes else "",
                "departments": ",".join(result.departments) if result.departments else "",
                "ontology_enrichment_failed": False,
            }
            vs.update_chunk_metadata(chunk_id, new_meta)
            if (i + 1) % 10 == 0:
                logger.info(f"  Processed [bold]{i + 1}[/bold] / {len(all_docs)}...")
        except Exception as e:
            logger.warning(f"  [red]✗[/red] Chunk {chunk_id} failed: {e}")

    logger.info(f"[green]✓[/green] Done — re-enriched [bold]{len(all_docs)}[/bold] chunks")


@cli.command()
def stats():
    """Show ontology enrichment statistics."""
    vs = VectorStore()
    all_docs = vs.get_all(limit=100000)

    if not all_docs:
        logger.info("[cyan]No documents in vector store[/cyan]")
        return

    total = len(all_docs)
    with_ontology = 0
    failed = 0

    for doc in all_docs:
        meta = doc.metadata
        concepts = meta.get("concepts") or meta.get("strategic_themes") or meta.get("departments")
        if concepts:
            with_ontology += 1
        if meta.get("ontology_enrichment_failed"):
            failed += 1

    logger.info(f"[bold]Ontology Enrichment Stats[/bold]")
    logger.info(f"  Total chunks:    [bold]{total}[/bold]")
    logger.info(f"  With ontology:   [green]{with_ontology}[/green]")
    logger.info(f"  Without ontology: [yellow]{total - with_ontology}[/yellow]")
    logger.info(f"  Failed:          [red]{failed}[/red]")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    cli()