import json
from langchain.prompts import PromptTemplate

# --- Prompt for keyword extraction ---
prompt = PromptTemplate.from_template(
    """You are a cybersecurity keyword extraction assistant.
The user query can describe an industry, attack type, loss impact, or context of a company.
You are to extract a concise keyword phrase (about 5 words) suitable for RAG retrieval and web search.

Return ONLY the keyword phrase.

User query: {query}
"""
)

def extract_query_params(llm, query: str) -> dict:
    """Use the LLM to extract only the keyword phrase from a query."""
    try:
        response = llm.invoke(prompt.format(query=query)) 
        return response.content.strip()  # Return as string
    except Exception as e:
        print(f"[ERROR] Failed to extract keywords: {e}")
        return query # Fallback to original query