"""Prompt templates for LLM."""
from typing import List, Dict, Any


def build_rag_prompt(query: str, context: List[Dict[str, Any]]) -> str:
    """Build a RAG prompt from query and context."""
    context_text = "\n\n".join([doc.get("content", "") for doc in context])
    
    prompt = f"""Based on the following context, please answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
    
    return prompt

