# ADR-002: Qdrant over Chroma for Vector Storage

## Status
**Accepted** | Date: 2025-05-20

## Context
We needed a vector database for the hybrid Knowledge Base that stores:
- Public SEC filings (10-K, 10-Q)
- Internal Nexlify Corp documents

Initially considered Chroma (local, simple) but needed more robust solution.

## Decision

We chose **Qdrant** with Docker deployment.

### Why Qdrant over Chroma?

| Factor | Chroma | Qdrant | Winner |
|--------|--------|--------|--------|
| Local dev | ✅ SQLite file | ✅ Docker container | Tie |
| Production scale | Limited | ✅ Full-featured | **Qdrant** |
| Hybrid search | Needs extra setup | ✅ Built-in sparse+dense | **Qdrant** |
| Metadata filtering | Simple dict | ✅ Full Filter API | **Qdrant** |
| Collection management | Single | ✅ Multiple collections | **Qdrant** |
| Installation | pip install | `docker pull` | Tie |

### Why NOT Qdrant local mode?

- Chroma local mode: `Chroma(persist_directory="...")` — single call
- Qdrant local mode: Requires manual collection creation

**Solution:** Use Qdrant Docker for both dev and production:
```bash
docker run -d --name nexlify-qdrant -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION                              │
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│   │ Ingestion    │───►│ VectorStore │───►│   Qdrant    │   │
│   │ (extractor)  │    │  (wrapper)   │    │  (Docker)   │   │
│   └──────────────┘    └──────────────┘    └──────────────┘   │
│                            │                    │            │
│                            ▼                    │            │
│                    ┌──────────────┐           │            │
│                    │  Chroma-like  │           │            │
│                    │     API      │◄──────────┘            │
│                    │  add/search  │                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### Key Differences from Chroma

1. **Collection Creation (Manual)**
   ```python
   # Chroma (auto-creates)
   Chroma(collection_name="docs", persist_directory="./chroma")
   
   # Qdrant (must create first)
   client.create_collection("docs", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
   ```

2. **ID Format (UUID required)**
   ```python
   # Chroma (string IDs OK)
   add_documents(ids=["doc_1", "doc_2"])
   
   # Qdrant (requires UUID or int)
   add_documents(ids=[str(uuid.uuid4()), ...])
   ```

3. **Metadata Filtering (nested key)**
   ```python
   # LangChain Qdrant stores metadata nested
   # Filter: is_public=True → metadata.is_public=True
   ```

### VectorStore Wrapper

We created `src/retrieval/vector_store.py` to provide Chroma-like API:

```python
from src.retrieval import VectorStore

vs = VectorStore(collection_name="nexlify_kb")

# Add documents (IDs auto-converted to UUID)
vs.add_documents(texts=[...], metadatas=[...], ids=["doc_1"])

# Search with filters
results = vs.search("revenue", k=5, filter={"is_public": True})
```

## Consequences

### Positive
1. **Production-ready** — Qdrant scales to billions of vectors
2. **Hybrid search ready** — Future sparse+dense built-in
3. **Rich filtering** — Full Filter API support
4. **Consistent API** — Wrapper provides simple interface

### Negative
1. **Docker required** — More complex than Chroma single file
2. **UUID IDs** — Must convert string IDs
3. **Nested metadata** — Filter keys need `metadata.` prefix

## Future Considerations

- [ ] Qdrant Cloud for production
- [ ] Hybrid search (sparse + dense) for keyword + semantic
- [ ] Multiple collections (public vs internal)
- [ ] ANM (Approximate Nearest Neighbor) tuning

## Related

- ADR-001: Unified Chunk Type
- Future ADR: Hybrid Search Strategy