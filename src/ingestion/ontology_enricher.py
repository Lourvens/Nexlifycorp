"""Ontology enrichment step — LLM-powered semantic metadata injection."""
import time

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from src.core.llm import get_llm
from src.ingestion.types import Chunk

logger = __import__("src.utils").utils.get_logger(__name__)


# =============================================================================
# TODO: SLM Integration for Cost Efficiency
# =============================================================================
# See docs/plans/slm-ontology-plan.md for the full plan.
#
# Currently using Claude Sonnet (frontier model) for high-quality structured
# output. This works well but costs ~$0.01-0.02 per chunk.
#
# Switching to a Small Language Model (SLM) like Qwen2.5-7B-Instruct could reduce
# cost to ~$0.001/chunk — 10-20x cheaper — with acceptable quality for this
# bounded extraction task.
#
# The switch involves:
#   1. Add ontology_provider (anthropic|huggingface) to config.py
#   2. Add HuggingFace LLM support to src/core/llm.py
#   3. Update _get_chain() to use the configured provider
#   4. Tune temperature for better JSON adherence on smaller models
#
# See slm-ontology-plan.md for candidate models and evaluation criteria.
# =============================================================================

ONTOLOGY_SYSTEM_PROMPT = """You are an expert financial and business analyst specializing in corporate SEC filings and enterprise documents. Your task is to analyze the provided text chunk and extract structured semantic metadata.

For each chunk, identify:
- **concepts**: Key business, financial, or technical concepts (e.g., revenue, margin expansion, AI investment, cybersecurity, competitive moat, supply chain risk, EPS, EBITDA, guidance)
- **strategic_themes**: Strategic themes and initiatives (e.g., growth, cost_efficiency, regulatory_compliance, market_expansion, innovation, risk_management, talent_acquisition, digital_transformation, geographic_expansion)
- **departments**: Departments or functions most relevant (e.g., finance, engineering, legal, sales, marketing, operations, HR, executive, product, security, R&D, supply_chain)

Guidelines:
- Be specific and concrete rather than generic
- Focus on concepts and themes actually discussed in the text
- Use lowercase with underscores for multi-word themes (e.g., cost_efficiency)
- Extract 2-8 concepts, 1-5 themes, 1-4 departments per chunk
- Only extract items that are explicitly mentioned or clearly implied
- Prioritize financial/business terminology over generic words"""


class OntologySchema(BaseModel):
    """Structured output schema for ontology enrichment."""

    concepts: list[str] = Field(
        description="Key business, financial, or technical concepts. "
        "Examples: revenue, margin_expansion, AI_investment, cybersecurity, competitive_moat, supply_chain_risk, EPS, EBITDA, guidance, market_share."
    )
    strategic_themes: list[str] = Field(
        description="Strategic themes and initiatives. "
        "Examples: growth, cost_efficiency, regulatory_compliance, market_expansion, innovation, risk_management, talent_acquisition, ESG, digital_transformation."
    )
    departments: list[str] = Field(
        description="Departments or functions most relevant to this content. "
        "Examples: finance, engineering, legal, sales, marketing, operations, HR, executive, product, security, RD, supply_chain."
    )


class OntologyEnrichmentStep:
    """
    Pluggable enrichment step that analyzes chunk content via LLM structured output
    and injects semantic metadata (concepts, strategic_themes, departments).

    Designed to be fail-open — if LLM calls fail, chunks continue through the pipeline
    with empty ontology fields and ontology_enrichment_failed=True.
    """

    MAX_RETRIES = 2
    CONTENT_MAX_TOKENS = 4000
    RETRY_BASE_DELAY = 2.0  # seconds

    def __init__(self, model: str | None = None):
        """
        Initialize the ontology enrichment step.

        Args:
            model: Optional model override. Defaults to config's anthropic_model.
        """
        self.model = model
        self._chain = None

    def _get_chain(self):
        """Get (or create) the LLM chain with system prompt + structured output. Lazily initialized."""
        if self._chain is None:
            llm = get_llm(model=self.model, temperature=0)

            prompt = ChatPromptTemplate.from_messages([
                ("system", ONTOLOGY_SYSTEM_PROMPT),
                ("human", "{content}"),
            ])

            self._chain = prompt | llm.with_structured_output(OntologySchema)
        return self._chain

    def process(self, chunk: Chunk) -> Chunk:
        """
        Enrich a single chunk with ontology metadata.

        Uses LLM structured output to extract concepts, strategic themes,
        and departments from the chunk content.

        Args:
            chunk: The chunk to enrich

        Returns:
            The same chunk with metadata fields populated
        """
        content = chunk.content[: self.CONTENT_MAX_TOKENS]
        chain = self._get_chain()

        logger.debug(
            f"[Ontology] Processing chunk [cyan]{chunk.metadata.chunk_id}[cyan] "
            f"(content length: {len(content)} chars)"
        )

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"[Ontology] Calling LLM for chunk [cyan]{chunk.metadata.chunk_id}[cyan] (attempt {attempt + 1}/{self.MAX_RETRIES})")
                result = chain.invoke({"content": content})

                if result is None:
                    raise ValueError("LLM returned None (possibly incomplete JSON or empty response)")

                logger.debug(
                    f"[Ontology] ✓ LLM response for [cyan]{chunk.metadata.chunk_id}[cyan]: "
                    f"{len(result.concepts)} concepts, {len(result.strategic_themes)} themes, {len(result.departments)} departments"
                )

                chunk.metadata.concepts = result.concepts
                chunk.metadata.strategic_themes = result.strategic_themes
                chunk.metadata.departments = result.departments
                return chunk
            except Exception as e:
                import traceback
                logger.warning(
                    f"[Ontology] ✗ Attempt {attempt + 1} failed for [cyan]{chunk.metadata.chunk_id}[cyan]: "
                    f"{type(e).__name__}: {e}\n    Traceback: {traceback.format_exc().strip()}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        f"[Ontology] ✗ Attempt {attempt + 1} failed for [cyan]{chunk.metadata.chunk_id}[cyan]: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.warning(
                        f"[Ontology] ✗ Permanently failed for [cyan]{chunk.metadata.chunk_id}[cyan] "
                        f"after {self.MAX_RETRIES} attempts: {type(e).__name__}: {e}\n"
                        f"    Last traceback: {traceback.format_exc().strip()}"
                    )
                    chunk.metadata.ontology_enrichment_failed = True
        return chunk

    def process_batch(self, chunks: list[Chunk]) -> list[Chunk]:
        """
        Enrich a batch of chunks with ontology metadata.

        Each chunk is processed independently. Failures are logged but do not
        stop processing of other chunks.

        Args:
            chunks: List of chunks to enrich

        Returns:
            The same list of chunks with metadata fields populated
        """
        logger.info(
            f"[Ontology] Starting batch enrichment of [bold]{len(chunks)}[/bold] chunks"
        )

        success_count = 0
        fail_count = 0

        for i, chunk in enumerate(chunks):
            logger.debug(f"[Ontology] Processing chunk {i + 1}/{len(chunks)}: [cyan]{chunk.metadata.chunk_id}[cyan]")
            self.process(chunk)

            if chunk.metadata.ontology_enrichment_failed:
                fail_count += 1
            else:
                success_count += 1

        logger.info(
            f"[Ontology] Batch complete: [green]{success_count}[/green] enriched, "
            f"[red]{fail_count}[/red] failed out of [bold]{len(chunks)}[/bold] total"
        )

        return chunks
