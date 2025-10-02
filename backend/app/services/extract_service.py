import json
from langchain.prompts import PromptTemplate

# --- Prompt for keyword and date extraction ---
prompt = PromptTemplate.from_template(
    """You are a cybersecurity keyword extraction assistant.
The user query describes an industry, attack type, loss impact, or timeline.
You are to extract keywords suitable for RAG retrieval and web search.

Extract:
- keywords: A concise phrase (2–5 words)
- start_date: (YYYY-MM-DD, default 2020-01-01 if not specified)
- end_date: (YYYY-MM-DD or null if not specified)

Return a JSON object with the following format:
{{
  "keywords": "keyword phrase",
  "start_date": "YYYY-MM-DD", // optional, default 2020-01-01
  "end_date": "YYYY-MM-DD", // optional, default None
}}
Do NOT include Markdown code fences (```json ... ```).

User query: {query}
"""
)

def extract_query_params(llm, query: str) -> dict:
    """Use the LLM to extract keywords + date range from a query."""
    response = llm.invoke(prompt.format(query=query))
    try:
        print(response.content) 
        return json.loads(response.content)
    except Exception as e:
        print(f"[ERROR] Failed to parse LLM output: {e}")
        return {"keywords": query, "start_date": "2020-01-01", "end_date": None}