"""Ingestion Manifest - Tracks documents that have been ingested."""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.utils.logger import logger


class IngestionManifest:
    """
    Tracks ingested documents to avoid re-ingesting.

    Manifest file: data/.ingestion_manifest.json
    """

    def __init__(self, manifest_path: Path | None = None):
        if manifest_path is None:
            from src.core.config import get_settings
            manifest_path = get_settings().ingestion_manifest_path
        self.manifest_path = Path(manifest_path)
        self._documents: dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        """Load manifest from JSON file."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._documents = data.get("documents", {})
                logger.info(f"[cyan]Loaded manifest:[/cyan] [bold]{len(self._documents)}[/bold] entries")
            except Exception as e:
                logger.warning(f"[yellow]Could not load manifest: {e}[yellow]")
                self._documents = {}
        else:
            self._documents = {}

    def save(self) -> None:
        """Save manifest to JSON file."""
        try:
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"documents": self._documents}
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"[red]Failed to save manifest: {e}[/red]")

    def is_ingested(self, doc_id: str) -> bool:
        """Check if document is already ingested."""
        return doc_id in self._documents

    def get(self, doc_id: str) -> Optional[dict]:
        """Get document metadata from manifest."""
        return self._documents.get(doc_id)

    def mark_ingested(
        self,
        doc_id: str,
        doc_type: str,
        chunks: int,
        **metadata,
    ) -> None:
        """Mark document as ingested."""
        self._documents[doc_id] = {
            "type": doc_type,
            "ingested_at": datetime.now().isoformat(),
            "chunks": chunks,
            **metadata,
        }
        self.save()

    def remove(self, doc_id: str) -> bool:
        """Remove document from manifest."""
        if doc_id in self._documents:
            del self._documents[doc_id]
            self.save()
            return True
        return False

    def list_by_type(self, doc_type: str) -> list[str]:
        """List all document IDs of a specific type."""
        return [
            doc_id
            for doc_id, info in self._documents.items()
            if info.get("type") == doc_type
        ]

    def list_all(self) -> list[tuple[str, dict]]:
        """List all documents with their metadata."""
        return list(self._documents.items())

    @property
    def count(self) -> int:
        """Total number of ingested documents."""
        return len(self._documents)


# Singleton instance
_manifest: Optional[IngestionManifest] = None


def get_manifest() -> IngestionManifest:
    """Get singleton manifest instance."""
    global _manifest
    if _manifest is None:
        _manifest = IngestionManifest()
    return _manifest