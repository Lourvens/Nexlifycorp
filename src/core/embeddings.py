"""Core embedding abstractions - not retrieval-specific."""
from abc import ABC, abstractmethod


class EmbeddingFunction(ABC):
    """Abstract base class for embedding functions."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        pass

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class LocalEmbeddingFunction(EmbeddingFunction):
    """Local embedding using sentence-transformers.

    No API required - runs entirely on local CPU/GPU.
    Model: all-MiniLM-L6-v2 (384 dimensions, ~90MB)
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize local embeddings."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-huggingface not installed. "
                "Run: uv add langchain-huggingface sentence-transformers"
            )

        self.model_name = model_name

        # Use LangChain's wrapper for sentence-transformers
        self._langchain_embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

        # all-MiniLM-L6-v2 outputs 384 dimensions
        self._dimension = 384

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        return self._langchain_embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        return self._langchain_embeddings.embed_query(text)


# =============================================================================
# FACTORY
# =============================================================================

_embedding_function: LocalEmbeddingFunction | None = None


def create_embedding_function() -> LocalEmbeddingFunction:
    """Create embedding function (always local for now)."""
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = LocalEmbeddingFunction()
    return _embedding_function


def get_embedding_dimension() -> int:
    """Get embedding dimension (384 for all-MiniLM-L6-v2)."""
    return 384
