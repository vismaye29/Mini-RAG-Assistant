"""
Embeddings Manager — Handles embedding generation and FAISS vector index
for semantic search, plus BM25 for keyword search.
Combines both using Reciprocal Rank Fusion (RRF) for Hybrid Search.
"""

import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

import config
from document_processor import DocumentChunk


class EmbeddingsManager:
    """
    Manages FAISS semantic search and BM25 keyword search.
    Supports persistence: save/load index + metadata to/from disk.
    """

    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.bm25: Optional[BM25Okapi] = None
        self.chunks_metadata: List[dict] = []  # Parallel list: metadata for each vector
        self.chunks_text: List[str] = []        # Parallel list: original text for each vector
        self._dimension = config.EMBEDDING_DIMENSION

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name, model_kwargs={"use_safetensors": False})
        return self.model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        """
        model = self._load_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,  # Normalize for cosine similarity via inner product
            batch_size=8,
        )
        return np.array(embeddings, dtype=np.float32)

    def build_index(self, chunks: List[DocumentChunk], progress_callback=None):
        """
        Build FAISS and BM25 indices from document chunks.
        """
        if not chunks:
            raise ValueError("No chunks provided to build index.")

        texts = [c.text for c in chunks]
        self.chunks_text = texts
        self.chunks_metadata = [c.metadata for c in chunks]

        # FAISS
        if progress_callback:
            progress_callback(35, 100, "Generating mathematical vectors (Embeddings)...")
        embeddings = self.embed_texts(texts)
        self._dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self._dimension)
        self.index.add(embeddings)

        # BM25
        if progress_callback:
            progress_callback(70, 100, "Building keyword search database (BM25)...")
        tokenized_corpus = [text.lower().split() for text in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = config.TOP_K,
        threshold: float = config.SIMILARITY_THRESHOLD,
        strategy: str = "hybrid",
    ) -> List[Tuple[str, dict, float]]:
        """
        Search using selected strategy: 'hybrid', 'semantic', or 'keyword'.
        """
        if self.index is None or self.index.ntotal == 0 or self.bm25 is None:
            return []

        fetch_k = top_k * 3
        faiss_results = []
        bm25_results = []

        # 1. FAISS Search
        if strategy in ["hybrid", "semantic"]:
            query_embedding = self.embed_texts([query])
            scores, indices = self.index.search(query_embedding, min(fetch_k, self.index.ntotal))
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= threshold:
                    faiss_results.append((idx, float(score)))

        # 2. BM25 Search
        if strategy in ["hybrid", "keyword"]:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            top_bm25_idx = np.argsort(bm25_scores)[::-1][:fetch_k]
            for idx in top_bm25_idx:
                if bm25_scores[idx] > 0:
                    bm25_results.append((idx, float(bm25_scores[idx])))

        # 3. Combine / Score
        results = []
        
        if strategy == "hybrid":
            # Reciprocal Rank Fusion
            rrf_scores = {}
            k_rrf = 60
            for rank, (idx, _) in enumerate(faiss_results):
                rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
            for rank, (idx, _) in enumerate(bm25_results):
                rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k_rrf + rank + 1)
                
            sorted_indices = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
            for idx, rrf_score in sorted_indices[:top_k]:
                results.append((self.chunks_text[idx], self.chunks_metadata[idx], rrf_score))

        elif strategy == "semantic":
            # Just use FAISS scores
            for idx, score in faiss_results[:top_k]:
                results.append((self.chunks_text[idx], self.chunks_metadata[idx], score))
                
        elif strategy == "keyword":
            # Just use BM25 scores
            for idx, score in bm25_results[:top_k]:
                results.append((self.chunks_text[idx], self.chunks_metadata[idx], score))

        return results

    def save(self, directory: str | Path = None, progress_callback=None):
        """Persist the FAISS index and metadata to disk."""
        if progress_callback:
            progress_callback(85, 100, "Saving database to disk...")
        directory = Path(directory) if directory else config.VECTOR_STORE_DIR
        directory.mkdir(parents=True, exist_ok=True)

        if self.index is not None:
            faiss.write_index(self.index, str(directory / "index.faiss"))

        meta = {
            "chunks_text": self.chunks_text,
            "chunks_metadata": self.chunks_metadata,
            "model_name": self.model_name,
            "dimension": self._dimension,
        }
        with open(directory / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def load(self, directory: str | Path = None) -> bool:
        """Load a persisted FAISS index, metadata, and rebuild BM25."""
        directory = Path(directory) if directory else config.VECTOR_STORE_DIR
        index_path = directory / "index.faiss"
        meta_path = directory / "metadata.json"

        if not index_path.exists() or not meta_path.exists():
            return False

        try:
            self.index = faiss.read_index(str(index_path))

            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            self.chunks_text = meta["chunks_text"]
            self.chunks_metadata = meta["chunks_metadata"]
            self.model_name = meta.get("model_name", config.EMBEDDING_MODEL_NAME)
            self._dimension = meta.get("dimension", config.EMBEDDING_DIMENSION)

            # Rebuild BM25 from texts
            tokenized_corpus = [text.lower().split() for text in self.chunks_text]
            self.bm25 = BM25Okapi(tokenized_corpus)

            return True
        except Exception as e:
            print(f"⚠️  Error loading index: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """Check if the index is built and ready for search."""
        return self.index is not None and self.index.ntotal > 0

    @property
    def total_vectors(self) -> int:
        """Number of vectors in the index."""
        return self.index.ntotal if self.index else 0
