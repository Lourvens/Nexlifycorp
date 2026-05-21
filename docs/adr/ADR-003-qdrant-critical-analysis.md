# ADR-003: Qdrant Vector Store - Critical Analysis & Corrected Implementation

**Date:** 2026-05-20  
**Status:** Approved  
**Author:** NexlifyCorp Agent

---

## Context

After initial implementation of the Qdrant vector store, a critical analysis revealed several issues with the metadata filtering approach and backward compatibility. This ADR documents the findings and the corrected implementation.

---

## Problems Identified

### Problem 1: Bad Practice - Attempting to Flatten Nested Metadata

**Initial approach:**
```python
# ❌ WRONG - Trying to "unwrap" nested metadata
flatten_metadata({"metadata": {"is_public": True}})
# Result: {"is_public": True}
```

**Why this was wrong:**
1. **Fight against the framework** - LangChain Qdrant intentionally stores metadata under a `metadata` key for consistency across ALL vector stores (Chroma, Pinecone, etc.)
2. **Leaky abstraction** - We were modifying how LangChain stores data internally, which could break on updates
3. **Unnecessary complexity** - The nested structure is the standard, not the exception

### Problem 2: Missing Backward Compatibility

**Issues:**
1. `_build_filter()` wasn't exported from `__init__.py`
2. Factory function `create_vector_store()` was missing from exports
3. Core utilities like `convert_filter_dict_to_qdrant()` were internal

### Problem 3: Incorrect Index Creation

```python
# ❌ WRONG - Indexing top-level 'is_public'
self._client.create_payload_index("is_public", ...)

# ✅ CORRECT - Indexing nested 'metadata.is_public'
self._client.create_payload_index("metadata.is_public", ...)
```

---

## Analysis: LangChain Qdrant Metadata Storage

After consulting official LangChain documentation and testing, here's how it works:

### How LangChain Qdrant Stores Data

```python
# When you add a document:
doc = Document(page_content="...", metadata={"is_public": True})

# LangChain Qdrant stores in Qdrant payload:
{
    "page_content": "...",
    "metadata": {
        "is_public": True
    }
}
```

### How to Filter Correctly

```python
# ❌ WRONG - Looking for top-level 'is_public'
Filter(must=[FieldCondition(key="is_public", match=MatchValue(value=True))])

# ✅ CORRECT - Using dot notation for nested metadata
Filter(must=[FieldCondition(key="metadata.is_public", match=MatchValue(value=True))])
```

### Why This Design?

1. **Consistency** - Same structure across all LangChain vector stores
2. **Separation** - Clear separation between content and metadata
3. **Compatibility** - Easy to migrate between vector stores
4. **LangChain convention** - `Document.page_content` and `Document.metadata`

---

## Corrected Implementation

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Keep nested metadata** | Follow LangChain convention |
| **Auto-prefix known fields** | `is_public` → `metadata.is_public` in filters |
| **Export utility functions** | Allow users to build their own filters |
| **Support both dict and Filter** | Backward compatibility with existing code |

### API Design

```python
# Simple usage (dict filter)
vs = VectorStore(collection_name="nexlify_kb")
results = vs.search("revenue", filter={"is_public": True})

# Advanced usage (Qdrant Filter)
from qdrant_client.models import Filter, FieldCondition, MatchValue
filter = Filter(must=[FieldCondition(key="metadata.is_public", match=MatchValue(value=True))])
results = vs.search("revenue", filter=filter)

# Utility for building filters
from src.retrieval import convert_filter_dict_to_qdrant
qdrant_filter = convert_filter_dict_to_qdrant({"content_type": "risk"})
```

---

## Metadata Filter Fields

Known metadata fields that get `metadata.` prefix:

```python
METADATA_FILTER_FIELDS = frozenset([
    "is_public",           # Access control
    "content_type",        # SEC: financial, risk, mda, etc.
    "ticker",              # Stock symbol
    "source_category",     # SEC_10K, INTERNAL_MEMO, etc.
    "classification",      # confidential, public, etc.
    "access_level",        # user access level
    "sec_form",            # 10-K, 10-Q, 8-K
    "sec_section",         # item1, item1a, etc.
    "internal_doc_type",   # board_memo, financial_review, etc.
    "fiscal_year",         # 2024, 2025
    "fiscal_quarter",      # Q1, Q2, Q3, Q4
    "document_id",         # Unique identifier
])
```

---

## Testing Results

### Filter Conversion
```python
# Dict filter -> Qdrant Filter
{'is_public': True}
  -> Filter(must=[FieldCondition(key='metadata.is_public', match=MatchValue(value=True))])

{'is_public': True, 'content_type': 'financial'}
  -> Filter(must=[
      FieldCondition(key='metadata.is_public', ...),
      FieldCondition(key='metadata.content_type', ...)
  ])
```

### End-to-End Search
```python
# Add documents
vs.add_documents(
    texts=['SEC filing shows revenue growth', 'Internal risk assessment'],
    metadatas=[
        {'is_public': True, 'content_type': 'financial'},
        {'is_public': False, 'content_type': 'risk'},
    ]
)

# Filter works correctly
results = vs.search('revenue', filter={'is_public': True})
# Returns: SEC filing document ✓

results = vs.search('risk', filter={'is_public': False})
# Returns: Internal risk document ✓
```

---

## Lessons Learned

1. **Don't fight the framework** - LangChain's nested metadata is intentional; work with it
2. **Test with real data** - Unit tests on empty collections don't catch filter issues
3. **Consult official docs** - Context7 documentation is more accurate than guessing
4. **Backward compatibility matters** - Export utilities, provide factory + singleton

---

## References

- [LangChain Qdrant Integration](https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant)
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/)
- [LangChain Vectorstore Best Practices](https://python.langchain.com/docs/modules/data_connection/vectorstores/)