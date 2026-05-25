"""
RAG Engine — Orchestrates the full Retrieval-Augmented Generation pipeline.
Ties together document processing, embeddings, retrieval, LLM generation,
and confidence scoring into a single high-level interface.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

import config
from document_processor import process_all_documents, process_document, DocumentChunk
from embeddings_manager import EmbeddingsManager
from llm_provider import get_provider, LLMProvider
from confidence_scorer import compute_confidence


@dataclass
class RAGResponse:
    """Structured response from the RAG engine."""
    answer: str
    sources: List[dict]
    confidence: dict
    metrics: dict = field(default_factory=dict)
    query: str = ""
    provider_name: str = ""


class RAGEngine:
    """
    Main orchestrator for the Mini-RAG Assistant.

    Usage:
        engine = RAGEngine()
        engine.ingest_documents()
        response = engine.query("What is the work from home policy?")
    """

    def __init__(self, provider_name: Optional[str] = None, model: Optional[str] = None):
        self.embeddings = EmbeddingsManager()
        self._provider_name = provider_name
        self._model = model
        self._llm: Optional[LLMProvider] = None
        self._chunks: List[DocumentChunk] = []
        self._ingested_files: List[str] = []

    @property
    def llm(self) -> LLMProvider:
        """Lazy-load the LLM provider."""
        if self._llm is None:
            self._llm = get_provider(self._provider_name, self._model)
        return self._llm

    def set_provider(self, provider_name: str, model: Optional[str] = None):
        """Switch the LLM provider at runtime."""
        self._provider_name = provider_name
        self._model = model
        self._llm = None  # Force re-creation

    def ingest_documents(self, directory: str | Path = None, progress_callback=None) -> dict:
        """
        Process all documents in the directory and rebuild the FAISS index.

        Args:
            directory: Path to document directory.
            progress_callback: Optional function(current, total, message)

        Returns:
            Dict with status, num_documents, num_chunks, message.
        """
        directory = Path(directory) if directory else config.DOCUMENTS_DIR
        chunks = process_all_documents(directory, progress_callback=progress_callback)

        if not chunks:
            return {
                "status": "error",
                "message": "No documents found or no text extracted.",
                "num_documents": 0,
                "num_chunks": 0,
            }

        self._chunks = chunks
        self._ingested_files = list(set(c.metadata["source_file"] for c in chunks))

        # Build FAISS index
        self.embeddings.build_index(chunks, progress_callback=progress_callback)
        # Persist to disk
        self.embeddings.save(progress_callback=progress_callback)
        
        if progress_callback:
            progress_callback(100, 100, "✅ Ingestion Complete!")

        return {
            "status": "success",
            "message": f"Ingested {len(self._ingested_files)} documents into {len(chunks)} chunks.",
            "num_documents": len(self._ingested_files),
            "num_chunks": len(chunks),
            "documents": self._ingested_files,
        }

    def ingest_single_document(self, pdf_path: str | Path) -> dict:
        """
        Add a single PDF to the existing index (re-builds the full index).

        Returns:
            Stats dict.
        """
        pdf_path = Path(pdf_path)
        new_chunks = process_document(pdf_path)
        self._chunks.extend(new_chunks)

        file_name = pdf_path.name
        if file_name not in self._ingested_files:
            self._ingested_files.append(file_name)

        # Rebuild full index (FAISS doesn't support incremental add with metadata tracking cleanly)
        self.embeddings.build_index(self._chunks)
        self.embeddings.save()

        return {
            "status": "success",
            "message": f"Added {file_name} ({len(new_chunks)} chunks). Total: {len(self._chunks)} chunks.",
            "num_documents": len(self._ingested_files),
            "num_chunks": len(self._chunks),
        }

    def load_index(self) -> bool:
        """Load a previously persisted FAISS index."""
        loaded = self.embeddings.load()
        if loaded:
            # Reconstruct ingested files list from metadata
            self._ingested_files = list(set(
                m.get("source_file", "") for m in self.embeddings.chunks_metadata
            ))
        return loaded

    def query(self, question: str, top_k: int = config.TOP_K, strategy: str = "hybrid") -> RAGResponse:
        """
        Answer a user question using the RAG pipeline.

        1. Retrieve relevant chunks from the FAISS index
        2. Build a context-augmented prompt
        3. Generate an answer using the LLM
        4. Compute confidence score

        Args:
            question: The user's natural-language question.
            top_k: Number of chunks to retrieve.
            strategy: 'hybrid', 'semantic', or 'keyword' search.

        Returns:
            RAGResponse with answer, confidence, and sources.
        """
        # Ensure index is ready
        if not self.embeddings.is_ready:
            loaded = self.load_index()
            if not loaded:
                return RAGResponse(
                    answer="⚠️ No documents have been ingested yet. Please upload or ingest documents first.",
                    sources=[],
                    confidence={"score": 0, "label": "No Data", "icon": "🔴", "breakdown": {}},
                    query=question,
                    provider_name="N/A",
                )

        # Step 1: Retrieve
        results = self.embeddings.search(question, top_k=top_k, strategy=strategy)

        if not results:
            return RAGResponse(
                answer="I couldn't find any relevant information in the knowledge base for your question. "
                       "Try rephrasing or asking about a topic covered in the uploaded documents.",
                sources=[],
                confidence={"score": 0, "label": "No Match", "icon": "🔴", "breakdown": {}},
                query=question,
                provider_name=self.llm.display_name,
            )

        # Deduplicate to parent chunks to ensure broad context and remove overlaps
        parent_results = []
        seen_parents = set()
        
        for text, meta, score in results:
            parent_id = meta.get("parent_id")
            parent_text = meta.get("parent_text", text)
            
            if parent_id:
                if parent_id in seen_parents:
                    continue
                seen_parents.add(parent_id)
                
            parent_results.append((parent_text, meta, score))

        # Step 2: Build augmented prompt
        context_block = self._build_context(parent_results)
        user_prompt = (
            f"Context from the knowledge base:\n"
            f"---\n{context_block}\n---\n\n"
            f"Question: {question}\n\n"
            f"Based on the above context, provide a detailed and accurate answer. "
            f"Cite the source document and page number for each piece of information."
        )

        # Step 3: Generate
        try:
            answer = self.llm.generate(user_prompt, system_prompt=config.SYSTEM_PROMPT)
        except Exception as e:
            answer = f"⚠️ LLM generation error: {str(e)}\n\nRetrieved context is shown below in the sources section."

        # Step 4: Confidence
        confidence = compute_confidence(question, parent_results, strategy=strategy)

        # Step 5: Build source citations
        formatted_sources = [
            {
                "text": p_text,
                "source_file": meta.get("source_file", "Unknown"),
                "page_number": meta.get("page_number", "?"),
                "similarity": round(score, 4),  # RRF scores are small floats, don't scale by 100
            }
            for p_text, meta, score in parent_results
        ]
        
        # Evaluate Retrieval live
        from evaluator import evaluate_retrieval_live
        retrieved_texts = [text for text, meta, score in parent_results]
        live_metrics = evaluate_retrieval_live(question, retrieved_texts, self.llm)

        return RAGResponse(
            answer=answer,
            sources=formatted_sources,
            confidence=confidence,
            metrics=live_metrics,
            query=question,
            provider_name=self.llm.display_name,
        )

    def _build_context(self, parent_results: list) -> str:
        """Format retrieved parent chunks into a context block for the LLM prompt."""
        parts = []
        for i, (text, meta, score) in enumerate(parent_results, 1):
            source = meta.get("source_file", "Unknown")
            page = meta.get("page_number", "?")
            parts.append(
                f"[Source {i}: {source}, Page {page} | RRF Score: {score:.4f}]\n{text}"
            )
        return "\n\n".join(parts)

    def get_stats(self) -> dict:
        """Return current engine statistics."""
        return {
            "index_ready": self.embeddings.is_ready,
            "total_vectors": self.embeddings.total_vectors,
            "ingested_files": self._ingested_files,
            "num_documents": len(self._ingested_files),
            "provider": self.llm.display_name if self._llm else "Not initialized",
        }
