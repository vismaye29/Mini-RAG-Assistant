import math
import json
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage

def calculate_mrr(retrieved_sources: List[str], expected_sources: List[str]) -> float:
    for i, src in enumerate(retrieved_sources):
        if src in expected_sources:
            return 1.0 / (i + 1)
    return 0.0

def calculate_precision_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
    if not retrieved_sources:
        return 0.0
    top_k = retrieved_sources[:k]
    relevant_count = sum(1 for src in top_k if src in expected_sources)
    return relevant_count / len(top_k) if top_k else 0.0

def calculate_recall_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
    if not expected_sources:
        return 0.0
    top_k = retrieved_sources[:k]
    found_expected = set(top_k).intersection(set(expected_sources))
    return len(found_expected) / len(set(expected_sources))

def calculate_ndcg(retrieved_sources: List[str], expected_sources: List[str]) -> float:
    dcg = 0.0
    for i, src in enumerate(retrieved_sources):
        if src in expected_sources:
            relevance = 1.0
            dcg += relevance / math.log2(i + 2) 
            
    idcg = 0.0
    for i in range(min(len(expected_sources), len(retrieved_sources))):
        idcg += 1.0 / math.log2(i + 2)
        
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

def evaluate_batch(queries_data: List[dict], rag_engine, top_k: int, strategy: str) -> dict:
    """
    Evaluates a batch of queries against the rag_engine.
    queries_data: [{'question': str, 'expected_sources': List[str]}]
    """
    total_mrr = 0.0
    total_precision = 0.0
    total_recall = 0.0
    total_ndcg = 0.0
    
    for item in queries_data:
        question = item["question"]
        expected_sources = item["expected_sources"]
        
        # Retrieve chunks (not deduplicated to parents, raw retrieval evaluation)
        results = rag_engine.embeddings.search(question, top_k=top_k, strategy=strategy)
        
        # Extract the source_files in order of retrieval
        retrieved_sources = []
        for text, meta, score in results:
            src = meta.get("source_file", "")
            if src not in retrieved_sources:
                retrieved_sources.append(src)
                
        total_mrr += calculate_mrr(retrieved_sources, expected_sources)
        total_precision += calculate_precision_at_k(retrieved_sources, expected_sources, top_k)
        total_recall += calculate_recall_at_k(retrieved_sources, expected_sources, top_k)
        total_ndcg += calculate_ndcg(retrieved_sources, expected_sources)
        
    n = len(queries_data)
    if n == 0:
        return {"mrr": 0, "precision": 0, "recall": 0, "ndcg": 0}
        
    return {
        "mrr": round(total_mrr / n, 3),
        "precision": round(total_precision / n, 3),
        "recall": round(total_recall / n, 3),
        "ndcg": round(total_ndcg / n, 3)
    }

def evaluate_retrieval_live(query: str, retrieved_texts: List[str], llm) -> dict:
    """
    Uses the LLM to grade retrieved chunks as 1 (relevant) or 0 (irrelevant) for the query.
    Calculates Pseudo-MRR, Pseudo-Precision, and Pseudo-NDCG based on the binary grades.
    """
    if not retrieved_texts:
        return {"mrr": 0.0, "precision": 0.0, "ndcg": 0.0}
        
    prompt = f"Query: {query}\n\n"
    for i, text in enumerate(retrieved_texts):
        prompt += f"Chunk {i+1}:\n{text}\n\n"
        
    system_msg = '''You are a STRICT expert evaluator. For each chunk provided, determine if it contains a DIRECT, FACTUAL, and COMPLETE answer to the query. 
If a chunk only provides partial context, tangential information, or is loosely related, assign it a 0.
Assign a 1 ONLY if the chunk thoroughly answers the query.
Output ONLY a JSON array of 1s and 0s corresponding to each chunk in order. 
Example Output: [1, 0, 0]'''
    
    try:
        content = llm.generate(user_prompt=prompt, system_prompt=system_msg).strip()
        
        # Use regex to find the first array of numbers in the response
        import re
        match = re.search(r'\[[\d\s,]+\]', content)
        if match:
            grades = json.loads(match.group(0))
        else:
            print(f"Failed to parse LLM evaluation response: {content}")
            grades = [0] * len(retrieved_texts)
        
        # Ensure grades match length of retrieved_texts
        if len(grades) != len(retrieved_texts):
            grades = grades[:len(retrieved_texts)] + [0] * max(0, len(retrieved_texts) - len(grades))
            
    except Exception as e:
        print(f"Error in LLM evaluation: {e}")
        grades = [0] * len(retrieved_texts)
        
    # Calculate MRR
    mrr = 0.0
    for i, g in enumerate(grades):
        if g == 1:
            mrr = 1.0 / (i + 1)
            break
            
    # Calculate Precision
    precision = sum(grades) / len(grades) if grades else 0.0
    
    # Calculate NDCG
    dcg = 0.0
    for i, g in enumerate(grades):
        if g == 1:
            dcg += 1.0 / math.log2(i + 2)
            
    num_relevant = sum(grades)
    idcg = 0.0
    for i in range(num_relevant):
        idcg += 1.0 / math.log2(i + 2)
        
    ndcg = dcg / idcg if idcg > 0 else 0.0
    
    return {
        "mrr": round(mrr, 3),
        "precision": round(precision, 3),
        "ndcg": round(ndcg, 3)
    }
