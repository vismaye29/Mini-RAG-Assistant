# 🧠 Mini-RAG Assistant

**Client Policy & Operations Knowledge Retrieval** — A lightweight Retrieval-Augmented Generation (RAG) prototype that answers employee questions using a local knowledge base of company documents.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT UI (app.py)                       │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│   │ Query Input  │  │ Answer Card  │  │ Source Citations Panel   │  │
│   │ + Chat Hist  │  │ + Confidence │  │ + Relevance % + Pages   │  │
│   └─────┬───────┘  └──────▲───────┘  └──────────▲───────────────┘  │
└─────────┼─────────────────┼──────────────────────┼──────────────────┘
          │                 │                      │
          ▼                 │                      │
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG ENGINE (rag_engine.py)                     │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────────┐   │
│  │  Document    │──▶│  Embeddings  │──▶│  FAISS Vector Index    │   │
│  │  Processor   │   │  Manager     │   │  (Persistence: disk)   │   │
│  │  (PyMuPDF)   │   │  (MiniLM)    │   │                        │   │
│  └─────────────┘   └──────┬───────┘   └──────────┬─────────────┘   │
│                           │ embed query           │ cosine search   │
│                           ▼                       ▼                 │
│                    ┌──────────────┐   ┌────────────────────────┐    │
│                    │  LLM Provider│   │  Confidence Scorer     │    │
│                    │  (OpenAI /   │   │  (Similarity + Coverage│    │
│                    │   Claude /   │   │   + Diversity)         │    │
│                    │   Ollama)    │   └────────────────────────┘    │
│                    └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 📋 Pipeline

1. **Ingest**: Parse PDFs (PyMuPDF) → Split into overlapping chunks (500 chars, 100 overlap) → Embed with `all-MiniLM-L6-v2` → Store in FAISS index
2. **Retrieve**: Embed user query → Cosine similarity search → Return top-5 chunks with scores
3. **Generate**: Build context-augmented prompt → LLM generates grounded answer with citations
4. **Score**: Compute confidence from retrieval similarity (50%), context coverage (30%), source diversity (20%)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ with conda
- At least one LLM backend:
  - **Ollama** (free, local): [Install Ollama](https://ollama.com) → `ollama pull llama3`
  - **OpenAI**: API key from [platform.openai.com](https://platform.openai.com)
  - **Anthropic**: API key from [console.anthropic.com](https://console.anthropic.com)

### Setup

```bash
# 1. Activate conda environment
conda activate py310

# 2. Install dependencies (most likely already installed)
pip install -r requirements.txt

# 3. Configure your LLM provider
cp .env.example .env
# Edit .env with your API keys / Ollama settings

# 4. Generate sample documents (optional)
python generate_sample_docs.py

# 5. Launch the app
streamlit run app.py
```

### First-Time Usage

1. Open the app in your browser (typically `http://localhost:8501`)
2. In the sidebar, select your LLM provider and model
3. Click **🚀 Build Index** to process and embed the documents
4. Start asking questions!

## 📄 Knowledge Base Documents

| Document | Domain | Topics Covered |
|----------|--------|----------------|
| `HR_Policy_Manual.pdf` | Human Resources | Leave policies, WFH, performance reviews, code of conduct, benefits, grievance procedures |
| `IT_Support_Process_Guide.pdf` | IT Operations | Ticket system, SLAs, access management, VPN setup, password policies, hardware provisioning |
| `Client_Onboarding_FAQ.pdf` | Client Services | Onboarding phases, KYC requirements, SLA tiers, data migration, training, go-live criteria |

## 💬 Example Queries

| Query | Expected Source |
|-------|----------------|
| "What is the company's work from home policy?" | HR_Policy_Manual.pdf |
| "How many sick leave days do I get per year?" | HR_Policy_Manual.pdf |
| "How do I raise an IT support ticket?" | IT_Support_Process_Guide.pdf |
| "What is the VPN server address?" | IT_Support_Process_Guide.pdf |
| "What documents are needed for client onboarding?" | Client_Onboarding_FAQ.pdf |
| "What happens during the hypercare period?" | Client_Onboarding_FAQ.pdf |

## 📊 Confidence Scoring

The confidence score (0-100%) combines three signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Retrieval Similarity | 50% | Average cosine similarity of retrieved chunks to the query |
| Context Coverage | 30% | Fraction of query terms found in the retrieved context |
| Source Diversity | 20% | Bonus for answers sourced from multiple documents |

**Labels**: 🟢 High (80-100%) · 🟡 Medium (50-79%) · 🔴 Low (0-49%)

## 🛠️ Tech Stack

- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local, free)
- **Vector Store**: FAISS (CPU)
- **LLM**: OpenAI / Anthropic Claude / Ollama (configurable)
- **PDF Parsing**: PyMuPDF (fitz)
- **Text Splitting**: LangChain RecursiveCharacterTextSplitter
- **UI**: Streamlit with custom CSS
- **Language**: Python 3.10

## 📁 Project Structure

```
V_rag/
├── app.py                       # Streamlit UI
├── rag_engine.py                # RAG pipeline orchestrator
├── document_processor.py        # PDF parsing + text chunking
├── embeddings_manager.py        # Embedding generation + FAISS index
├── llm_provider.py              # Multi-backend LLM abstraction
├── confidence_scorer.py         # Confidence scoring logic
├── config.py                    # Configuration and constants
├── generate_sample_docs.py      # Sample PDF generator
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variable template
├── README.md                    # This file
├── documents/                   # PDF knowledge base
│   ├── HR_Policy_Manual.pdf
│   ├── IT_Support_Process_Guide.pdf
│   └── Client_Onboarding_FAQ.pdf
└── vector_store/                # Persisted FAISS index (auto-created)
```
