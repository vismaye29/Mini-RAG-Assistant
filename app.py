"""
Mini-RAG Assistant — Streamlit UI
A premium, dark-themed interface for the RAG-powered knowledge retrieval system.
"""

import os
# Fix protobuf/tensorflow compatibility issue BEFORE ANY other imports (like streamlit)
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
os.environ.setdefault("USE_TF", "0")

import streamlit as st
import time
from pathlib import Path

import config
from rag_engine import RAGEngine


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Mini-RAG Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — Premium Dark Theme
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ────────────────────────────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header ────────────────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .main-header h1 {
        color: #fff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin: 0;
        font-weight: 300;
    }

    /* ── Info Icon & Tooltip ───────────────────────────────────────── */
    .info-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        cursor: pointer;
        position: relative;
        transition: background 0.2s;
    }
    .info-icon:hover {
        background: rgba(255,255,255,0.2);
    }
    .info-icon:hover .stats-tooltip {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }
    .stats-tooltip {
        position: absolute;
        top: 100%;
        right: 0;
        margin-top: 12px;
        background: #1e1e2e;
        border: 1px solid rgba(102,126,234,0.4);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        width: 320px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        opacity: 0;
        visibility: hidden;
        transform: translateY(-10px);
        transition: all 0.2s ease;
        z-index: 1000;
        cursor: default;
    }
    .tooltip-stat {
        background: rgba(255,255,255,0.03);
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    .tooltip-stat-val {
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .tooltip-stat-label {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 5px 0 0 0;
    }

    /* ── Answer Card ───────────────────────────────────────────────── */
    .answer-card {
        background: linear-gradient(145deg, #1a1a2e, #252540);
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    }
    .answer-card h3 {
        color: #667eea;
        font-weight: 600;
        margin-top: 0;
    }

    /* ── Confidence Bar ────────────────────────────────────────────── */
    .confidence-container {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .confidence-bar-bg {
        background: rgba(255,255,255,0.08);
        border-radius: 20px;
        height: 12px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 20px;
        transition: width 1s ease;
    }
    .confidence-high { background: linear-gradient(90deg, #00b894, #00cec9); }
    .confidence-medium { background: linear-gradient(90deg, #fdcb6e, #e17055); }
    .confidence-low { background: linear-gradient(90deg, #e17055, #d63031); }

    /* ── Source Cards ───────────────────────────────────────────────── */
    .source-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        transition: border-color 0.2s ease;
    }
    .source-card:hover {
        border-color: rgba(102,126,234,0.4);
    }
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 0.5rem;
    }
    .source-page {
        display: inline-block;
        background: rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.7);
        font-size: 0.7rem;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.5rem;
    }
    .source-relevance {
        display: inline-block;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.5);
    }
    .source-text {
        margin-top: 0.7rem;
        padding: 0.8rem 1rem;
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
        font-size: 0.88rem;
        line-height: 1.6;
        color: rgba(255,255,255,0.75);
        border-left: 3px solid #667eea;
    }

    /* ── Sidebar Styling ───────────────────────────────────────────── */
    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    .sidebar-header h2 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
        margin: 0;
    }

    /* ── Chat History ──────────────────────────────────────────────── */
    .history-item {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .history-question {
        color: #667eea;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .history-answer {
        color: rgba(255,255,255,0.6);
        font-size: 0.82rem;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════
if "engine" not in st.session_state:
    engine = RAGEngine()
    st.session_state.engine = engine
    
    # Auto-load the vector store if it exists
    if engine.load_index():
        st.session_state.index_ready = True
        st.session_state.ingest_stats = engine.get_stats()
    else:
        st.session_state.index_ready = False
        st.session_state.ingest_stats = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tracks which docs were most recently uploaded — used to auto-scope queries
if "uploaded_doc_scope" not in st.session_state:
    st.session_state.uploaded_doc_scope = []


def get_engine() -> RAGEngine:
    return st.session_state.engine


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>⚙️ Configuration</h2>
    </div>
    """, unsafe_allow_html=True)

    # ── LLM Provider ──
    st.markdown("#### LLM Provider")
    provider_choice = st.selectbox(
        "Select Provider",
        options=["openai"],
        index=0,
        help="Choose the LLM backend for answer generation.",
        label_visibility="collapsed",
    )

    model_defaults = {
        "ollama": config.OLLAMA_MODEL,
        "openai": config.OPENAI_MODEL,
        "anthropic": config.ANTHROPIC_MODEL,
    }
    model_name = st.text_input(
        "Model Name",
        value=model_defaults.get(provider_choice, ""),
        help="Override the default model name.",
    )

    # Apply provider change
    engine = get_engine()
    engine.set_provider(provider_choice, model_name if model_name else None)

    st.divider()

    # ── Document Management ──
    st.markdown("#### 📄 Documents")

    # Upload new PDFs
    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload PDF documents to add to the knowledge base.",
    )

    if uploaded_files:
        new_files = False
        uploaded_names = []
        for uploaded_file in uploaded_files:
            uploaded_names.append(uploaded_file.name)
            # Check if this file is already in the database to avoid infinite rebuilding
            if uploaded_file.name not in st.session_state.ingest_stats.get("ingested_files", []):
                new_files = True
                
            save_path = config.DOCUMENTS_DIR / uploaded_file.name
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
        if new_files:
            st.success(f"✅ Saved {len(uploaded_files)} file(s)")
            progress_bar = st.progress(0, text="Initializing auto-indexing...")
            
            def update_progress(current, total, message):
                pct = min(int((current / total) * 100), 100)
                progress_bar.progress(pct, text=message)
                
            stats = engine.ingest_documents(progress_callback=update_progress)
            progress_bar.empty()
            
            st.session_state.ingest_stats = stats
            if stats["status"] == "success":
                st.session_state.index_ready = True
                # Auto-scope to the uploaded files
                st.session_state.uploaded_doc_scope = uploaded_names
                st.success("✅ Index automatically updated!")
            else:
                st.error(f"❌ {stats['message']}")

    # List existing documents
    existing_pdfs = sorted(config.DOCUMENTS_DIR.glob("*.pdf"))
    if existing_pdfs:
        st.markdown(f"**{len(existing_pdfs)} documents available:**")
        for pdf in existing_pdfs:
            size_kb = pdf.stat().st_size / 1024
            st.markdown(f"📄 `{pdf.name}` ({size_kb:.0f} KB)")
    else:
        st.info("No documents found. Upload PDFs or place them in the `documents/` folder.")

    st.divider()

    # ── Ingest Button ──
    st.markdown("#### Index Management")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Build Index", use_container_width=True, type="primary"):
            progress_bar = st.progress(0, text="Initializing database build...")
            def update_progress(current, total, message):
                pct = min(int((current / total) * 100), 100)
                progress_bar.progress(pct, text=message)
                
            stats = engine.ingest_documents(progress_callback=update_progress)
            progress_bar.empty()
            
            st.session_state.ingest_stats = stats
            if stats["status"] == "success":
                st.session_state.index_ready = True
                st.success(f"✅ {stats['message']}")
            else:
                st.error(f"❌ {stats['message']}")

    with col2:
        if st.button("Load Index", use_container_width=True):
            loaded = engine.load_index()
            if loaded:
                st.session_state.index_ready = True
                st.session_state.ingest_stats = engine.get_stats()
                st.success("✅ Index loaded from disk")
            else:
                st.warning("No saved index found. Build one first.")

    # ── Retrieval Settings ──
    st.divider()
    st.markdown("#### 🔍 Retrieval Settings")
    
    search_strategy_label = st.selectbox(
        "Search Strategy",
        options=["Hybrid (FAISS + BM25)", "Semantic Only (FAISS)", "Keyword Only (BM25)"],
        index=0,
        help="Choose the algorithm used to search the documents.",
        label_visibility="collapsed"
    )
    
    strategy_map = {
        "Hybrid (FAISS + BM25)": "hybrid",
        "Semantic Only (FAISS)": "semantic",
        "Keyword Only (BM25)": "keyword",
    }
    search_strategy = strategy_map[search_strategy_label]

    top_k = st.slider("Top-K Results", min_value=1, max_value=15, value=config.TOP_K, step=1)

    # ── Document Scope Filter ──
    st.divider()
    st.markdown("#### 🎯 Document Scope")

    all_docs = sorted([pdf.name for pdf in config.DOCUMENTS_DIR.glob("*.pdf")])

    # Filter out any stale names that no longer exist on disk
    valid_scope = [d for d in st.session_state.uploaded_doc_scope if d in all_docs]
    st.session_state.uploaded_doc_scope = valid_scope

    selected_docs = st.multiselect(
        "Scope",
        options=all_docs,
        default=valid_scope,
        help="Automatically set to uploaded files. Clear to search all documents.",
        label_visibility="collapsed",
        placeholder="All documents (no filter)",
        key="doc_scope_select",
    )

    # Sync manual changes back to session state
    st.session_state.uploaded_doc_scope = selected_docs

    if selected_docs:
        st.info(f"🎯 Scoped to **{len(selected_docs)}** doc(s): {', '.join(selected_docs)}")
        if st.button("🔓 Search All Documents", use_container_width=True):
            st.session_state.uploaded_doc_scope = []
            st.rerun()
    else:
        st.caption("Searching across all documents.")

    st.divider()
    st.markdown(
        "<p style='text-align:center; color:rgba(255,255,255,0.3); font-size:0.75rem;'>"
        "Mini-RAG Assistant v1.0</p>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

# ── Header & Stats Hover ──
engine = get_engine()
stats = st.session_state.ingest_stats
n_docs = stats.get("num_documents", 0)
n_chunks = stats.get("num_chunks", engine.embeddings.total_vectors)
status_text = "Ready ✅" if st.session_state.index_ready else "Not Built"
prov = provider_choice.title()

st.markdown(f"""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1>Mini-RAG Assistant</h1>
            <p>Client Policy & Operations Knowledge Retrieval — powered by RAG</p>
        </div>
        <div class="info-icon">
            <i>i</i>
            <div class="stats-tooltip">
                <div class="tooltip-stat">
                    <p class="tooltip-stat-val">{n_docs}</p>
                    <p class="tooltip-stat-label">Documents</p>
                </div>
                <div class="tooltip-stat">
                    <p class="tooltip-stat-val">{n_chunks}</p>
                    <p class="tooltip-stat-label">Chunks Indexed</p>
                </div>
                <div class="tooltip-stat">
                    <p class="tooltip-stat-val">{status_text}</p>
                    <p class="tooltip-stat-label">Index Status</p>
                </div>
                <div class="tooltip-stat">
                    <p class="tooltip-stat-val">{prov}</p>
                    <p class="tooltip-stat-label">LLM Provider</p>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ═══════════════════════════════════════════════════════════════════════════════
# QUERY INPUT
# ═══════════════════════════════════════════════════════════════════════════════
query = st.chat_input(
    placeholder="Ask a question about policies, IT support, or client onboarding...",
)

if query:
    if not st.session_state.index_ready:
        # Try loading from disk
        if engine.load_index():
            st.session_state.index_ready = True
            st.session_state.ingest_stats = engine.get_stats()
        else:
            st.warning("⚠️ Please build or load the index first using the sidebar controls.")
            st.stop()

    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base & generating answer..."):
            start_time = time.time()
            response = engine.query(
                query,
                top_k=top_k,
                strategy=search_strategy,
                filter_files=selected_docs if selected_docs else None,
            )
            elapsed = time.time() - start_time

        metrics = getattr(response, "metrics", {})
        metrics_html = ""
        if metrics:
            metrics_html = f"""
<div style="display:flex; gap:1.5rem; margin-top:1rem; padding-top:1rem; border-top:1px dashed rgba(255,255,255,0.1); font-size:0.85rem; color:rgba(255,255,255,0.7);">
    <div title="Mean Reciprocal Rank"><strong>MRR:</strong> {metrics.get('mrr', 0):.3f}</div>
    <div title="Precision@K"><strong>Precision:</strong> {metrics.get('precision', 0):.3f}</div>
    <div title="Normalized Discounted Cumulative Gain"><strong>NDCG:</strong> {metrics.get('ndcg', 0):.3f}</div>
    <div title="Recall requires ground truth dataset"><strong>Recall:</strong> N/A</div>
</div>
"""

        # ── Answer ──
        st.markdown(f"""
<div class="answer-card">
    <h3>Answer</h3>
    <div class="answer-text">{response.answer}</div>
    {metrics_html}
<p style="margin-top:1rem; color:rgba(255,255,255,0.35); font-size:0.75rem;">
Generated by {response.provider_name} in {elapsed:.1f}s
</p>
</div>
""", unsafe_allow_html=True)

        # ── Confidence Score ──
        conf = response.confidence
        score = conf.get("score", 0)
        label = conf.get("label", "N/A")
        icon = conf.get("icon", "")
        breakdown = conf.get("breakdown", {})

        css_class = "confidence-high" if score >= 80 else ("confidence-medium" if score >= 50 else "confidence-low")

        st.markdown(f"""
        <div class="confidence-container">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; color:rgba(255,255,255,0.8);">
                    {icon} Confidence: {score}% — {label}
                </span>
            </div>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill {css_class}" style="width:{score}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Breakdown expander
        with st.expander("📊 Confidence Breakdown"):
            b_cols = st.columns(3)
            with b_cols[0]:
                st.metric("Retrieval Similarity", f"{breakdown.get('retrieval_similarity', 0)}%")
            with b_cols[1]:
                st.metric("Context Coverage", f"{breakdown.get('context_coverage', 0)}%")
            with b_cols[2]:
                st.metric("Source Diversity", f"{breakdown.get('source_diversity', 0)}%")

        # ── Source Citations ──
        if response.sources:
            with st.expander(f"📚 Source Citations ({len(response.sources)} passages)", expanded=True):
                for i, src in enumerate(response.sources, 1):
                    file_name = src["source_file"]
                    page = src["page_number"]
                    relevance = src["similarity"]
                    text = src["text"]

                    # Extract query keywords for highlighting (excluding stopwords)
                    import re
                    stopwords = {"and", "the", "for", "with", "how", "does", "what", "are", "you", "that", "this", "from", "across", "about", "your", "can"}
                    query_terms = set(
                        word.lower() for word in re.findall(r'\b\w+\b', query) 
                        if len(word) > 2 and word.lower() not in stopwords
                    )
                    
                    # Truncate and highlight
                    highlighted_text = text[:500] + ('...' if len(text) > 500 else '')
                    for term in query_terms:
                        pattern = re.compile(rf'\b({re.escape(term)})\b', re.IGNORECASE)
                        highlighted_text = pattern.sub(
                            lambda m: f"<mark style='background-color:rgba(255, 235, 59, 0.4); color:white; border-radius:3px; padding:0 2px;'>{m.group(0)}</mark>", 
                            highlighted_text
                        )

                    # Color-code file badges
                    badge_colors = {
                        "HR_Policy_Manual.pdf": "#00b894",
                        "IT_Support_Process_Guide.pdf": "#0984e3",
                        "Client_Onboarding_FAQ.pdf": "#6c5ce7",
                    }
                    color = badge_colors.get(file_name, "#667eea")

                    st.markdown(f"""
                    <div class="source-card">
                        <span class="source-badge" style="background:{color};">{file_name}</span>
                        <span class="source-page">📄 Page {page}</span>
                        <span class="source-relevance">🎯 {relevance}% match</span>
                        <div class="source-text">{highlighted_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Store in chat history
    st.session_state.chat_history.append({
        "query": query,
        "answer": response.answer[:200],
        "confidence": response.confidence.get("score", 0),
    })

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY (below the main query area)
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.chat_history:
    st.divider()
    st.markdown("### 📜 Conversation History")
    for item in reversed(st.session_state.chat_history[:-1] if query else st.session_state.chat_history):
        conf_val = item.get("confidence", 0)
        conf_icon = "🟢" if conf_val >= 80 else ("🟡" if conf_val >= 50 else "🔴")
        st.markdown(f"""
        <div class="history-item">
            <div class="history-question">❓ {item['query']}</div>
            <div class="history-answer">{item['answer'][:150]}... {conf_icon} {conf_val}%</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("📊 System Evaluation (Benchmark Dashboard)"):
    st.markdown("Run a predefined set of queries to evaluate the exact MRR, Recall, Precision, and NDCG of the current search strategy against a ground-truth dataset.")
    
    if st.button("Run Benchmark Evaluation", use_container_width=True):
        import json
        from evaluator import evaluate_batch
        
        try:
            with open("tests/benchmark_data.json", "r", encoding="utf-8") as f:
                queries_data = json.load(f)
                
            with st.spinner(f"Evaluating {len(queries_data)} queries using {search_strategy_label}..."):
                metrics = evaluate_batch(queries_data, engine, top_k=top_k, strategy=search_strategy)
                
            col_m, col_p, col_r, col_n = st.columns(4)
            col_m.metric("MRR", f"{metrics['mrr']:.3f}")
            col_p.metric(f"Precision@{top_k}", f"{metrics['precision']:.3f}")
            col_r.metric(f"Recall@{top_k}", f"{metrics['recall']:.3f}")
            col_n.metric("NDCG", f"{metrics['ndcg']:.3f}")
            
            st.success("✅ Evaluation complete!")
        except FileNotFoundError:
            st.error("⚠️ `tests/benchmark_data.json` not found. Please create the ground truth dataset first.")
