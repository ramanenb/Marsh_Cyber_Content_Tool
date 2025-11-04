import json
from app.models.tool_model import TavilyInput
from langchain_tavily import TavilySearch

def tavily_search(args) -> str:
    """Run Tavily search with dynamic inputs and extract affected organizations."""
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return []

    args = TavilyInput(**args)

    query = args.query
    start_date = args.start_date
    end_date = args.end_date
    industries = args.industries
    
    # Removed as relevance of returned news articles is lower
    # Add industries to query for better context
    # if industries and len(industries) > 0:
    #     joined_industries = ", ".join(industries)
    #     query = f"Industries: {joined_industries}. {query}"
    
    print(f"[DEBUG tavily] query={query}, start_date={start_date}, end_date={end_date}")
    tavily = TavilySearch(
        max_results=5,
        topic="general",
        start_date=start_date,
        end_date=end_date,
        include_domains=[
            "bleepingcomputer.com",
            "thecyberwire.com",
            "thehackernews.com",
            "therecord.media",
            "databreachtoday.com",
            "databreaches.net",
            "techtarget.com"
        ],
    )
    articles = tavily.invoke({"query": query}).get("results")

    print(json.dumps(articles, indent=2, ensure_ascii=False))
    return articles