"""
Document Processor — PDF parsing and text chunking for the RAG pipeline.
Uses PyMuPDF (fitz) for robust text extraction and LangChain's
RecursiveCharacterTextSplitter for intelligent chunking.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


@dataclass
class DocumentChunk:
    """Represents a single chunk of text with its metadata."""
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}


class PDFProcessor:
    """Extracts text from PDF files using PyMuPDF."""

    @staticmethod
    def extract_text(pdf_path: str | Path) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF file, returning a list of page dicts.

        Returns:
            List of dicts with keys: 'text', 'page_number', 'source_file'
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pages = []
        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    pages.append({
                        "text": text.strip(),
                        "page_number": page_num + 1,
                        "source_file": pdf_path.name,
                    })
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Error processing {pdf_path.name}: {e}")

        return pages


class TextChunker:
    """Splits extracted text into overlapping chunks for embedding."""

    def __init__(
        self,
        parent_chunk_size: int = 1500,
        parent_chunk_overlap: int = 300,
        child_chunk_size: int = 300,
        child_chunk_overlap: int = 50,
    ):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Split page-level text into overlapping chunks, preserving metadata.
        Uses a Parent-Child strategy: large parent chunks are created for context,
        and smaller child chunks are created for precise embedding retrieval.

        Args:
            pages: Output from PDFProcessor.extract_text()

        Returns:
            List of DocumentChunk objects with metadata attached.
        """
        all_child_chunks: List[DocumentChunk] = []
        global_parent_index = 0

        for page_data in pages:
            text = page_data["text"]
            parent_splits = self.parent_splitter.split_text(text)

            for parent_text in parent_splits:
                parent_id = f"parent_{global_parent_index}_{page_data['source_file']}"
                global_parent_index += 1
                
                # Split parent into children
                child_splits = self.child_splitter.split_text(parent_text)
                
                for child_idx, child_text in enumerate(child_splits):
                    chunk = DocumentChunk(
                        text=child_text,
                        metadata={
                            "source_file": page_data["source_file"],
                            "page_number": page_data["page_number"],
                            "parent_id": parent_id,
                            "parent_text": parent_text,
                            "child_index": child_idx,
                        },
                    )
                    all_child_chunks.append(chunk)

        # Add total_chunks to each chunk's metadata
        for chunk in all_child_chunks:
            chunk.metadata["total_chunks"] = len(all_child_chunks)

        return all_child_chunks


def process_document(pdf_path: str | Path) -> List[DocumentChunk]:
    """
    End-to-end document processing: extract text from PDF and chunk it.

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        List of DocumentChunk objects ready for embedding.
    """
    processor = PDFProcessor()
    chunker = TextChunker()

    pages = processor.extract_text(pdf_path)
    chunks = chunker.chunk_pages(pages)

    return chunks


def process_all_documents(
    directory: str | Path = None,
    progress_callback=None
) -> List[DocumentChunk]:
    """
    Process all PDF files in the given directory.

    Args:
        directory: Path to directory containing PDFs. Defaults to config.DOCUMENTS_DIR.
        progress_callback: Optional function(current, total, message) to report progress.

    Returns:
        Combined list of DocumentChunk objects from all PDFs.
    """
    directory = Path(directory) if directory else config.DOCUMENTS_DIR

    if not directory.exists():
        raise FileNotFoundError(f"Documents directory not found: {directory}")

    all_chunks: List[DocumentChunk] = []
    pdf_files = sorted(directory.glob("*.pdf"))
    total_files = len(pdf_files)

    if not pdf_files:
        return all_chunks

    for i, pdf_path in enumerate(pdf_files):
        if progress_callback:
            # We reserve the first 30% of the progress bar for reading/chunking
            # e.g., if there are 2 files, file 1 is 0/2 -> 0%, file 2 is 1/2 -> 15%, done is 30%
            progress_callback(int((i / total_files) * 30), 100, f"Reading & chunking {pdf_path.name}...")
        try:
            chunks = process_document(pdf_path)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"⚠️  Skipping {pdf_path.name}: {e}")

    if progress_callback:
        progress_callback(30, 100, f"Finished extracting {len(all_chunks)} chunks.")

    return all_chunks
