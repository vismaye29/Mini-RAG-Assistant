"""
Build Vector Store — Processes all PDFs in the documents/ folder,
generates embeddings, and saves a FAISS index + metadata to vector_store/.
"""

import os
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from document_processor import process_all_documents
from embeddings_manager import EmbeddingsManager
import config


def main():
    print("=" * 60)
    print("  FAISS Vector Store Builder")
    print("=" * 60)

    # Step 1: Process all PDFs in documents/
    print(f"\n[DIR] Scanning documents in: {config.DOCUMENTS_DIR}")
    pdf_files = sorted(config.DOCUMENTS_DIR.glob("*.pdf"))
    print(f"   Found {len(pdf_files)} PDF file(s):")
    for f in pdf_files:
        size_kb = f.stat().st_size / 1024
        print(f"     - {f.name} ({size_kb:.1f} KB)")

    print(f"\n[DOC] Processing documents (chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})...")
    chunks = process_all_documents()

    if not chunks:
        print("[FAIL] No chunks generated. Check that documents/ contains valid PDFs.")
        return

    print(f"   [OK] Generated {len(chunks)} chunks from {len(pdf_files)} document(s)")

    # Show per-document breakdown
    from collections import Counter
    source_counts = Counter(c.metadata["source_file"] for c in chunks)
    for source, count in source_counts.items():
        print(f"     - {source}: {count} chunks")

    # Step 2: Build FAISS index
    print(f"\n[BUILD] Building FAISS index using model: {config.EMBEDDING_MODEL_NAME}")
    manager = EmbeddingsManager()
    manager.build_index(chunks)
    print(f"   [OK] Index built with {manager.total_vectors} vectors (dim={config.EMBEDDING_DIMENSION})")

    # Step 3: Save to disk
    print(f"\n[SAVE] Saving vector store to: {config.VECTOR_STORE_DIR}")
    manager.save()

    # Verify saved files
    index_file = config.VECTOR_STORE_DIR / "index.faiss"
    meta_file = config.VECTOR_STORE_DIR / "metadata.json"
    print(f"   [OK] index.faiss  ({index_file.stat().st_size / 1024:.1f} KB)")
    print(f"   [OK] metadata.json ({meta_file.stat().st_size / 1024:.1f} KB)")

    # Step 4: Verify by loading it back
    print("\n[VERIFY] Verifying: loading index back from disk...")
    test_manager = EmbeddingsManager()
    loaded = test_manager.load()
    if loaded and test_manager.is_ready:
        print(f"   [OK] Verified! {test_manager.total_vectors} vectors loaded successfully.")
    else:
        print("   [FAIL] Verification failed -- could not reload the index.")

    print("\n" + "=" * 60)
    print("  Done! Vector store is ready for RAG queries.")
    print("=" * 60)


if __name__ == "__main__":
    main()
