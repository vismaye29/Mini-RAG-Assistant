"""
Configuration and constants for the Mini-RAG Assistant.
Centralizes all tunable parameters for document processing,
embedding, retrieval, and LLM generation.
"""

import os

# Fix protobuf/tensorflow compatibility issue (TF 2.10 + protobuf 6.x)
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
os.environ.setdefault("USE_TF", "0")
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
DOCUMENTS_DIR = BASE_DIR / "documents"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

# Auto-create directories
DOCUMENTS_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# ── Document Processing ─────────────────────────────────────────────────────
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 100       # Overlap between consecutive chunks
SUPPORTED_EXTENSIONS = [".pdf"]

# ── Embedding Model ─────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384   # Dimension for all-MiniLM-L6-v2

# ── Retrieval ────────────────────────────────────────────────────────────────
TOP_K = 5                 # Number of chunks to retrieve per query
SIMILARITY_THRESHOLD = 0.25  # Minimum cosine similarity to include a chunk

# ── LLM Provider Settings ───────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "openai", "anthropic", "ollama"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a knowledgeable assistant for a consulting firm. Your role is to answer questions accurately using ONLY the provided context from the company's knowledge base.

Rules:
1. Answer ONLY based on the provided context. Do not use external knowledge.
2. If the context does not contain enough information to answer, say "I don't have enough information in the knowledge base to answer this question accurately."
3. When referencing information, cite the source document and page number.
4. Be concise but thorough. Use bullet points for multi-part answers.
5. If the question spans multiple documents, synthesize information from all relevant sources.
"""

# ── Confidence Scoring ───────────────────────────────────────────────────────
CONFIDENCE_WEIGHTS = {
    "retrieval_similarity": 0.50,   # Weight for average cosine similarity
    "context_coverage": 0.30,       # Weight for query term coverage
    "source_diversity": 0.20,       # Weight for multi-document sourcing
}

CONFIDENCE_LABELS = {
    (80, 101): ("High", "🟢"),
    (50, 80):  ("Medium", "🟡"),
    (0, 50):   ("Low", "🔴"),
}
