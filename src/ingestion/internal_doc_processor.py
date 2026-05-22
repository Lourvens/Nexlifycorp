"""Internal Document Extractor for Nexlify Corp."""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.ingestion.types import InternalSection, InternalDocument
from src.utils.logger import logger

DEFAULT_OUTPUT_DIR = Path("data/extracted/internal")

# Document type mapping from folder structure
DOCUMENT_TYPES = {
    "risk-registers": "Risk Register",
    "board-memos": "Board Memo",
    "product-roadmaps": "Product Roadmap",
    "financial-reviews": "Financial Review",
    "supply-chain": "Supply Chain Assessment",
    "competitor-analyses": "Competitor Analysis",
    "policies": "Policy",
    "earnings-prep": "Earnings Preparation",
}


def extract_sections_from_markdown(filepath: Path) -> list[dict]:
    """
    Extract sections based on Markdown headers.

    Args:
        filepath: Path to the Markdown file

    Returns:
        List of section dicts with title, level, text
    """
    content = filepath.read_text(encoding="utf-8")

    # Pattern: ## or ### followed by text
    header_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

    headers = []

    for match in header_pattern.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        headers.append((level, match.start(), title))

    # Extract content between headers
    sections = []

    for i, (level, start, title) in enumerate(headers):
        end = headers[i + 1][1] if i + 1 < len(headers) else len(content)
        section_text = content[start:end].strip()

        # Remove the header line from content
        lines = section_text.split("\n", 1)
        if lines[0].startswith("#"):
            section_text = lines[1].strip() if len(lines) > 1 else ""

        sections.append(
            {
                "title": title,
                "level": level,
                "text": section_text,
            }
        )

    return sections


def parse_metadata_from_header(content: str) -> dict:
    """
    Parse document metadata from the header table.

    Args:
        content: First part of the document containing header

    Returns:
        Dict with document_id, date, version, classification
    """
    metadata = {
        "document_id": None,
        "date": None,
        "version": None,
        "classification": "CONFIDENTIAL",
    }

    # Look for table rows like | **Field** | Value | or | Field | Value |
    table_pattern = re.compile(
        r"^\|\s*(?:\*\*)?([^|\n]+?)(?:\*\*)?\s*\|\s*([^|\n]+?)\s*\|\s*$",
        re.MULTILINE,
    )

    for match in table_pattern.finditer(content[:2500]):
        field = match.group(1).strip().lower().replace(" ", "_").replace(r"*", "")
        value = match.group(2).strip()

        if field == "document_id":
            metadata["document_id"] = value
        elif field == "date":
            # Try to parse date
            for fmt in ["%B %d, %Y", "%Y-%m-%d", "%B %d, %Y"]:
                try:
                    metadata["date"] = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
        elif field == "version":
            metadata["version"] = value
        elif field == "classification":
            metadata["classification"] = value.upper()

    return metadata


def extract_topics(text: str) -> list[str]:
    """
    Auto-extract keywords/topics from text.

    Args:
        text: Section text

    Returns:
        List of keywords
    """
    # Common tech/finance keywords to look for
    keywords = {
        "NEXL-X3",
        "NEXL-X4",
        "NEXL-A3",
        "NVIDIA",
        "AMD",
        "TSMC",
        "AI",
        "GPU",
        "inference",
        "training",
        "revenue",
        "margin",
        "supply chain",
        "Taiwan",
        "automotive",
        "edge",
        "data center",
        "HBM",
        "CoWoS",
        "risk",
        "competition",
    }

    found = []
    text_upper = text.upper()

    for keyword in keywords:
        if keyword.upper() in text_upper:
            found.append(keyword)

    return found[:10]  # Limit to 10 topics


def has_financials(text: str) -> bool:
    """Check if section contains financial data."""
    # Look for dollar signs, percentages, billion/million
    patterns = [
        r"\$[\d,]+",
        r"\d+\.\d+%",
        r"\$[\d.]+\s*[BbMm]",
        r"revenue",
        r"income",
        r"margin",
        r"assets",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def has_projections(text: str) -> bool:
    """Check if section contains forward-looking projections."""
    patterns = [
        r"expect",
        r"forecast",
        r"project",
        r"target",
        r"plan",
        r"will",
        r"outlook",
        r"anticipate",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_internal_document(
    filepath: Path,
    document_type: str,
) -> Optional[InternalDocument]:
    """
    Extract an internal document from a Markdown file.

    Args:
        filepath: Path to the Markdown file
        document_type: Type of document (from folder name)

    Returns:
        InternalDocument with sections, or None if error
    """
    try:
        content = filepath.read_text(encoding="utf-8")

        # Parse document metadata
        doc_metadata = parse_metadata_from_header(content)

        # Extract sections
        sections = extract_sections_from_markdown(filepath)

        # Build InternalSection objects
        internal_sections = []

        for i, section in enumerate(sections):
            # Build section path (parent headers)
            section_path = section["title"]

            # Get parent H2 if this is H3
            if section["level"] == 3 and i > 0:
                for j in range(i - 1, -1, -1):
                    if sections[j]["level"] == 2:
                        section_path = f"{sections[j]['title']} / {section['title']}"
                        break

            internal_section = InternalSection(
                title=section["title"],
                content=section["text"][:50000] if len(section["text"]) > 50000 else section["text"],
                level=section["level"],
                document_type=document_type,
                document_id=doc_metadata.get("document_id"),
                classification=doc_metadata.get("classification", "CONFIDENTIAL"),
                date=doc_metadata.get("date"),
                section_path=section_path,
                topics=extract_topics(section["text"]),
                contains_financials=has_financials(section["text"]),
                contains_projections=has_projections(section["text"]),
            )

            internal_sections.append(internal_section)

        return InternalDocument(sections=internal_sections)

    except Exception as e:
        logger.error(f"[red]✗[/red] Error extracting [cyan]{filepath}[cyan]: {e}")
        return None


def extract_internal_document_from_content(
    content: str,
    doc_id: str,
    document_type: str,
) -> Optional[InternalDocument]:
    """
    Extract an internal document from a content string.

    Args:
        content: Markdown content as string
        doc_id: Document ID
        document_type: Type of document (e.g., "board_memo")

    Returns:
        InternalDocument with sections, or None if error
    """
    try:
        # Parse document metadata
        doc_metadata = parse_metadata_from_header(content)

        # Extract sections using temp file approach for code reuse
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            delete=False,
            encoding='utf-8'
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            sections = extract_sections_from_markdown(tmp_path)
        finally:
            os.unlink(tmp_path)

        # Build InternalSection objects
        internal_sections = []

        for i, section in enumerate(sections):
            # Build section path (parent headers)
            section_path = section["title"]

            # Get parent H2 if this is H3
            if section["level"] == 3 and i > 0:
                for j in range(i - 1, -1, -1):
                    if sections[j]["level"] == 2:
                        section_path = f"{sections[j]['title']} / {section['title']}"
                        break

            internal_section = InternalSection(
                title=section["title"],
                content=section["text"][:50000] if len(section["text"]) > 50000 else section["text"],
                level=section["level"],
                document_type=document_type,
                document_id=doc_id or doc_metadata.get("document_id"),
                classification=doc_metadata.get("classification", "CONFIDENTIAL"),
                date=doc_metadata.get("date"),
                section_path=section_path,
                topics=extract_topics(section["text"]),
                contains_financials=has_financials(section["text"]),
                contains_projections=has_projections(section["text"]),
            )

            internal_sections.append(internal_section)

        return InternalDocument(sections=internal_sections)

    except Exception as e:
        logger.error(f"[red]✗[/red] Error extracting internal doc from content: {e}")
        return None


def extract_all_internal_documents(
    base_path: Path = Path("data/internal"),
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> list[InternalDocument]:
    """
    Extract all internal documents from the internal folder structure.

    Args:
        base_path: Path to data/internal directory
        output_dir: Path to save extracted JSON files

    Returns:
        List of all extracted InternalDocument objects
    """
    documents = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for folder_name, doc_type in DOCUMENT_TYPES.items():
        folder_path = base_path / folder_name

        if not folder_path.exists():
            logger.warning(f"[yellow]Folder not found:[/yellow] [dim]{folder_path}[dim]")
            continue

        # Process all markdown files in folder
        for md_file in folder_path.glob("*.md"):
            doc = extract_internal_document(md_file, doc_type)

            if doc:
                documents.append(doc)

                # Save to disk
                doc_id = doc.metadata.get("document_id", md_file.stem)
                filename = f"{folder_name}_{doc_id}.json"
                filepath = output_dir / filename

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(
                        [s.model_dump() for s in doc.sections],
                        f,
                        indent=2,
                        default=str,
                    )

                logger.info(f"[green]✓[/green] Extracted [cyan]{md_file.name}[cyan] ([bold]{len(doc.sections)}[/bold] sections)")

    logger.info(f"[bold]Total extracted:[/bold] [bold]{len(documents)}[/bold] documents")
    return documents


if __name__ == "__main__":
    # Test extraction
    from src.utils.logger import logger

    logger.info("Testing internal document extraction...")

    docs = extract_all_internal_documents()

    logger.info(f"Extracted {len(docs)} documents")

    if docs:
        for doc in docs[:2]:
            meta = doc.metadata
            logger.info(f"\n{meta['document_type']}: {meta['document_id']}")
            logger.info(f"  Sections: {len(doc.sections)}")
            logger.info(f"  Classification: {meta['classification']}")