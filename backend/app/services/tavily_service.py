import json
from app.models.tool_model import TavilyInput
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from app.config.settings import llm
import re

def extract_organization_from_article(title: str, content: str) -> str:
    """Extract the main affected organization from article title and content using LLM"""
    prompt = f"""
    Extract the main company or organization that was affected by the cybersecurity incident from this article.
    Return ONLY the company name, no additional text or explanation.
    If no clear organization is mentioned, return "UNKNOWN".

    Title: {title}
    Content: {content[:1000]}...

    Company name:
    """

    try:
        response = llm([HumanMessage(content=prompt)])
        org_name = response.content.strip()
        # Clean up common suffixes and prefixes
        org_name = re.sub(r'\b(Inc|Corp|Corporation|Ltd|Limited|Company|Co)\b\.?', '', org_name, flags=re.IGNORECASE).strip()
        return org_name if org_name and org_name != "UNKNOWN" else "UNKNOWN"
    except Exception as e:
        print(f"Error extracting organization: {e}")
        return "UNKNOWN"

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
    #industries = args.industries

    #print(f"[DEBUG tavily] query={query}, start_date={start_date}, end_date={end_date}")
    tavily = TavilySearch(
        max_results=5,
        topic="general",
        start_date=start_date,
        end_date=end_date,
        include_domains=[
            "bleepingcomputer.com",
            "securityweek.com",
            "thecyberwire.com",
            "thehackernews.com",
            "therecord.media",
            "databreachtoday.com",
            "databreaches.net"
        ],
    )
    articles = tavily.invoke({"query": query}).get("results")

    # Enhance articles with affected organization
    enhanced_articles = []
    for article in articles:
        enhanced_article = article.copy()
        # Extract affected organization
        affected_org = extract_organization_from_article(
            article.get("title", ""),
            article.get("content", "")
        )
        enhanced_article["affected_organization"] = affected_org
        enhanced_articles.append(enhanced_article)

    print(json.dumps(enhanced_articles, indent=2, ensure_ascii=False))
    return enhanced_articles