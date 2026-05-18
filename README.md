# Nexlify KB Agent - AI Financial Analyst Assistant

An enterprise-grade **hybrid Knowledge Base + Agentic AI system** for a fictional company **Nexlify Corp** (Ticker: NEXL).

The system combines **real public SEC EDGAR filings** with **fictional internal enterprise documents** to simulate real-world financial intelligence, compliance, and research workflows.

**Goal**: Progressively build a production-ready Knowledge Base (RAG → Hybrid → GraphRAG → Agentic) while learning LangChain, LangGraph, metadata governance, and enterprise architecture decisions.

---

## 🎯 Project Objectives

- Master hybrid Knowledge Base design (public + private data)
- Practice enterprise-grade patterns: metadata filtering, RBAC simulation, versioning, governance
- Build from basic RAG → advanced Agentic system using **LangChain + LangGraph**
- Develop strong architecture decision-making skills for real enterprise use cases
- Create a compelling portfolio project for AI Engineer / FinTech roles

---

## 🛠 Tech Stack

- **Framework**: LangChain + LangGraph
- **Vector Store**: Chroma (Day 1–7), later Weaviate / Pinecone / Databricks Vector Search
- **LLMs**: Ollama (local) → Groq / OpenAI / Anthropic
- **Graph DB**: Neo4j (from Day 8)
- **Document Processing**: Unstructured, pypdf, sec-edgar-downloader
- **UI**: Streamlit or Gradio
- **Evaluation**: Ragas / LangSmith
- **Future**: Databricks Lakehouse + Mosaic AI

---

## 📁 Project Structure

```bash
nexlify-kb-agent/
├── data/
│   ├── public/           # Real SEC 10-K, 10-Q filings
│   └── internal/         # Fictional Nexlify Corp documents
├── src/
│   ├── ingestion/        # Loading & processing pipelines
│   ├── retrieval/        # RAG, Hybrid, GraphRAG retrievers
│   ├── agents/           # LangGraph agents & workflows
│   ├── evaluation/       # Ragas, metrics, testing
│   └── utils/            # Helpers, metadata tools
├── notebooks/            # Experiments & daily notes
├── streamlit_app/        # UI (from Day 3+)
├── docs/                 # Architecture Decision Records (ADRs)
├── .env
├── requirements.txt
├── README.md
└── main.py               # Entry point
```

---

## 🚀 Quick Setup

### 1. Clone & Environment

```bash
git clone <your-repo-url>
cd nexlify-kb-agent
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core requirements** (add more as we progress):

```txt
langchain
langchain-community
langchain-openai
langchain-ollama
langchain-chroma
langgraph
langsmith
sec-edgar-downloader
unstructured[all-docs]
pypdf
chromadb
streamlit
ragas
python-dotenv
```

### 3. Environment Variables (`.env`)

```env
OLLAMA_MODEL=llama3.1:8b
# OPENAI_API_KEY=sk-...
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=...
```

### 4. Download Public Data (Run once)

```bash
python src/ingestion/download_filings.py
```

---

## 📅 Learning Path & Daily Progress

This project follows a structured **Day-by-Day** plan:

| Days       | Focus                              | Key Deliverables                     |
|------------|------------------------------------|--------------------------------------|
| 1–3        | Basic Hybrid RAG                   | Ingestion + metadata filtering       |
| 4–7        | Production RAG                     | Hybrid search, reranking, evaluation |
| 8–12       | Knowledge Graphs + GraphRAG        | Neo4j, multi-hop reasoning           |
| 13–18      | Agentic RAG & LangGraph            | Multi-step & multi-agent workflows   |
| 19–25+     | Enterprise Architecture & Polish   | Governance, scaling, ADRs            |

**How to use this README**:
- Complete one day at a time.
- Create a branch `day-01`, `day-02`, etc. or use clear commits.
- Update the **Progress Log** section below daily.

---

## 📊 Progress Log

- [ ] Day 1: Basic Hybrid Ingestion + Metadata RAG
- [ ] Day 2: ...
- [ ] ...

---

## 🧪 How to Run

```bash
# Run basic query test
python src/test_query.py

# Launch UI (when ready)
streamlit run streamlit_app/app.py
```

---

## 📝 Architecture Decision Records (ADRs)

All major decisions will be documented in `/docs/adr/`

Examples:
- ADR-001: Choice of Metadata Strategy
- ADR-002: Vector Store Comparison
- ADR-003: When to use GraphRAG vs Agentic RAG

---

## 🔮 Future Enhancements (Production Path)

- Migrate to **Databricks Lakehouse** (Unity Catalog + Mosaic AI Vector Search)
- Add structured data (Delta Tables for financial metrics)
- Deploy agents as serving endpoints
- Full evaluation dashboard + monitoring
- Multi-user RBAC simulation

---

## 📚 Learning Resources

- LangChain Docs: https://python.langchain.com
- LangGraph: https://langchain-ai.github.io/langgraph/
- SEC EDGAR Filing Structure
- "Building Production RAG Systems" (various blogs & papers)

---

## 💡 Tips for Success

1. Always attach rich metadata when ingesting documents.
2. Test with both simple and complex questions daily.
3. Keep detailed notes in `notebooks/` about what worked and what didn't.
4. Focus on **why** you make each architecture choice.
5. Commit often with meaningful messages.

---

**Project Status**: In Progress
**Current Day**: Day 1

---

*Built as a structured learning journey for mastering Knowledge Bases in the Agentic Era.*