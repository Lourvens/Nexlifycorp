"""
Ingestion Pipeline - Orchestrates Extract → Chunk → Store flow.

Single entry point for ingesting documents into the vector store:
- SEC filings: extract from EDGAR → chunk → store
- Internal docs: extract from Markdown → chunk → store

Usage:
    from src.ingestion import IngestionPipeline, create_ingestion_pipeline

    pipeline = create_ingestion_pipeline()
    count = pipeline.ingest_sec_filing("NVDA", 2024)
    count = pipeline.ingest_internal_doc("NBPQ4-2025-001", "board_memo", content)
"""
from typing import Optional

from src.ingestion.types import Chunk
from src.ingestion.sec_filing_extractor import extract_10k, extract_10q
from src.ingestion.internal_doc_processor import extract_internal_document
from src.ingestion.chunk_strategies.sec_chunker import SECChunker
from src.ingestion.chunk_strategies.internal_chunker import InternalChunker
from src.ingestion.manifest import get_manifest
from src.utils.logger import logger

# Optional ontology enrichment (lazy import to avoid hard dependency)
try:
    from src.ingestion.ontology_enricher import OntologyEnrichmentStep
    ONTOLOGY_AVAILABLE = True
except ImportError:
    ONTOLOGY_AVAILABLE = False
    OntologyEnrichmentStep = None

# Forward reference to avoid circular import
VectorStore = "VectorStore"


def _get_doc_id(ticker: str, form: str, year: int | None) -> str:
    """Generate document ID for SEC filings."""
    year_str = str(year) if year else "latest"
    return f"{ticker}_{form.replace('-', '')}_{year_str}"


class IngestionPipeline:
    """
    Orchestrates the full ingestion pipeline: Extract → Chunk → Store.

    Two operation modes:
    - process_* : Extract + chunk, return Chunks (no side effects, testable)
    - ingest_*  : Full pipeline, store to vector store (side effects)
    """

    def __init__(self, vector_store: VectorStore, enable_ontology: bool = False):
        """
        Initialize pipeline with vector store.

        Args:
            vector_store: VectorStore instance for storage
            enable_ontology: If True, enable LLM-powered ontology enrichment
        """
        self.vector_store = vector_store
        self._ontology_step: OntologyEnrichmentStep | None = None
        if enable_ontology and ONTOLOGY_AVAILABLE:
            self._ontology_step = OntologyEnrichmentStep()
            logger.debug("Ontology enrichment enabled")
        elif enable_ontology and not ONTOLOGY_AVAILABLE:
            logger.warning("enable_ontology=True but ontology_enricher not available")

    # =========================================================================
    # SEC Filing Processing
    # =========================================================================

    def process_sec_filing(
        self,
        ticker: str,
        year: int | None = None,
        form: str = "10-K",
    ) -> list[Chunk]:
        """
        Extract SEC filing and chunk into list[Chunk].

        Args:
            ticker: Stock ticker (e.g., "NVDA")
            year: Fiscal year (None for latest)
            form: "10-K" or "10-Q"

        Returns:
            List of Chunk objects ready for embedding
        """
        # Extract from EDGAR
        if form == "10-K":
            sec_doc = extract_10k(ticker, year)
        else:
            sec_doc = extract_10q(ticker, year)

        if not sec_doc:
            logger.warning(f"[yellow]No {form} found for {ticker}[yellow]")
            return []

        # Chunk the document
        chunker = SECChunker(
            ticker=sec_doc.metadata.ticker,
            form=form,
            fiscal_year=sec_doc.metadata.fiscal_year or year or 2024,
            cik=sec_doc.metadata.cik,
        )

        chunks = []
        for section in sec_doc.sections:
            section_chunks = chunker.chunk_section(section)
            chunks.extend(section_chunks)

        logger.info(f"[cyan]Processed {ticker} {form}[cyan]: [bold]{len(chunks)}[/bold] chunks")
        return chunks

    def ingest_sec_filing(
        self,
        ticker: str,
        year: int | None = None,
        form: str = "10-K",
    ) -> int:
        """
        Full pipeline: Extract → Chunk → Store.

        Args:
            ticker: Stock ticker
            year: Fiscal year (None for latest)
            form: "10-K" or "10-Q"

        Returns:
            Number of chunks stored
        """
        # Check manifest
        doc_id = _get_doc_id(ticker, form, year)
        manifest = get_manifest()

        if manifest.is_ingested(doc_id):
            logger.info(f"[cyan]Skipping[/cyan] [cyan]{ticker} {form}[cyan] (already ingested)")
            return 0

        chunks = self.process_sec_filing(ticker, year, form)
        if chunks:
            self.vector_store.add_chunks(chunks)
            # Ontology enrichment (after store, no re-embed needed)
            if self._ontology_step is not None:
                self._ontology_step.process_batch(chunks)
                for chunk in chunks:
                    self.vector_store.update_chunk_metadata(
                        chunk.metadata.chunk_id,
                        chunk.metadata.model_dump(mode="json"),
                    )
            manifest.mark_ingested(
                doc_id=doc_id,
                doc_type="sec",
                chunks=len(chunks),
                ticker=ticker,
                form=form,
                year=year,
            )
            logger.info(f"[green]✓[/green] Ingested [bold]{len(chunks)}[/bold] chunks for [cyan]{ticker} {form}[cyan]")
        return len(chunks)

    # =========================================================================
    # Internal Document Processing
    # =========================================================================

    def process_internal_doc(
        self,
        doc_id: str,
        doc_type: str,
        content: str,
    ) -> list[Chunk]:
        """
        Parse internal markdown doc and chunk into list[Chunk].

        Args:
            doc_id: Document ID (e.g., "NBPQ4-2025-001")
            doc_type: Document type (e.g., "board_memo", "risk_register")
            content: Markdown content string

        Returns:
            List of Chunk objects ready for embedding
        """
        from src.ingestion.internal_doc_processor import extract_internal_document_from_content

        internal_doc = extract_internal_document_from_content(content, doc_id, doc_type)
        if not internal_doc:
            logger.warning(f"[yellow]Failed to parse internal doc {doc_id}[yellow]")
            return []

        # Get classification from first non-H1 section
        classification = "CONFIDENTIAL"
        for section in internal_doc.sections:
            if section.level != 1 and section.classification:
                classification = section.classification
                break

        chunker = InternalChunker(
            doc_id=doc_id,
            doc_type=doc_type,
            classification=classification,
        )

        chunks = chunker.chunk_document(internal_doc)
        logger.info(f"[cyan]Processed internal doc {doc_id}[cyan]: [bold]{len(chunks)}[/bold] chunks")
        return chunks

    def ingest_internal_doc(
        self,
        doc_id: str,
        doc_type: str,
        content: str,
    ) -> int:
        """
        Full pipeline: Parse → Chunk → Store.

        Args:
            doc_id: Document ID
            doc_type: Document type
            content: Markdown content

        Returns:
            Number of chunks stored
        """
        # Check manifest
        manifest = get_manifest()

        if manifest.is_ingested(doc_id):
            logger.info(f"[cyan]Skipping[/cyan] [yellow]{doc_id}[yellow] (already ingested)")
            return 0

        chunks = self.process_internal_doc(doc_id, doc_type, content)
        if chunks:
            self.vector_store.add_chunks(chunks)
            # Ontology enrichment (after store, no re-embed needed)
            if self._ontology_step is not None:
                self._ontology_step.process_batch(chunks)
                for chunk in chunks:
                    self.vector_store.update_chunk_metadata(
                        chunk.metadata.chunk_id,
                        chunk.metadata.model_dump(mode="json"),
                    )
            manifest.mark_ingested(
                doc_id=doc_id,
                doc_type="internal",
                chunks=len(chunks),
                internal_doc_type=doc_type,
            )
            logger.info(f"[green]✓[/green] Ingested [bold]{len(chunks)}[/bold] chunks for internal doc [yellow]{doc_id}[yellow]")
        return len(chunks)

    # =========================================================================
    # Batch Operations
    # =========================================================================

    def ingest_multiple_sec_filings(
        self,
        filings: list[tuple[str, int | None, str]],
    ) -> dict[str, int]:
        """
        Ingest multiple SEC filings.

        Args:
            filings: List of (ticker, year, form) tuples

        Returns:
            Dict mapping ticker→chunk count
        """
        results = {}
        for ticker, year, form in filings:
            try:
                count = self.ingest_sec_filing(ticker, year, form)
                results[ticker] = count
            except Exception as e:
                logger.error(f"[red]✗[/red] Failed to ingest {ticker} {form}: {e}")
                results[ticker] = 0
        return results


# =============================================================================
# Factory
# =============================================================================

_pipeline: Optional[IngestionPipeline] = None


def create_ingestion_pipeline(
    vector_store: "VectorStore | None" = None,
    *,
    enable_ontology: bool | None = None,
    **vector_store_kwargs,
) -> IngestionPipeline:
    """
    Factory to create IngestionPipeline.

    Args:
        vector_store: Optional VectorStore instance (creates if not provided)
        enable_ontology: If None, reads from settings (ENABLE_ONTOLOGY env var).
                         If True/False, overrides settings.
        **vector_store_kwargs: Passed to VectorStore if created

    Returns:
        IngestionPipeline instance
    """
    if vector_store is None:
        from src.core import VectorStore
        vector_store = VectorStore(**vector_store_kwargs)

    # Default to settings value if not explicitly passed
    if enable_ontology is None:
        from src.core.config import get_settings
        enable_ontology = get_settings().enable_ontology

    return IngestionPipeline(vector_store, enable_ontology=enable_ontology)


def get_ingestion_pipeline() -> IngestionPipeline:
    """Get singleton pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = create_ingestion_pipeline()
    return _pipeline


def reset_ingestion_pipeline() -> None:
    """Reset singleton."""
    global _pipeline
    _pipeline = None