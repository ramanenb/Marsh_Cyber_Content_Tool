import time
from app.config.settings import llm
from langchain_core.messages import HumanMessage, SystemMessage
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader
import asyncio
import nest_asyncio
nest_asyncio.apply()

def is_specific_event(article: dict) -> bool:
    """Return True if the articles describes only one specific cybersecurity incident."""
    title = article["title"]
    content = article["content"]
    prompt = f"""
    Given the following article title and preview, return True if it described only one specific cybersecurity incident or event,
    return False if it is a generic article.
    Title: {title}
    Preview: {content}
    """
    response = llm([HumanMessage(content=prompt)])
    print(f"{title}: {response.content}")
    return response.content.strip().lower().startswith("true")

def clean_webpage_text(raw_text: str, starts_at: str) -> str:
    """Use an LLM to clean webpage text, keeping only the actual article body."""
    messages = [
        SystemMessage(content=(
            "You are an assistant that extracts only the actual article body text from a webpage. "
            "Remove navigation menus, headers, footers, advertisements, unrelated article titles, "
            "and irrelevant boilerplate. Only keep the clean article text."
        )),
        HumanMessage(content=(
            f"Extracted webpage text:\n\n{raw_text}\n\n"
            f"The article should start at:\n\n{starts_at}\n\n"
            "Return ONLY the cleaned article text, nothing else."
        ))
    ]
    response = llm(messages)
    return response.content.strip()

async def fetch_full_text_async(url: str, starts_at: str) -> str:
    """Async load full article text using WebBaseLoader."""
    BLOCKED_DOMAINS = [
        "darkreading.com",
    ]
    print(f"Fetching url: {url}")
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    if domain in BLOCKED_DOMAINS:
        print(f"[INFO] Skipping blocked domain: {domain}")
        return starts_at # returns back original article["content"]

    try:
        loader = WebBaseLoader(url, show_progress=True, continue_on_failure=True)
        docs = loader.aload()
        raw_text = " ".join(doc.page_content for doc in docs)
        clean_text = clean_webpage_text(raw_text, starts_at)
        return clean_text
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return ""

async def process_result_async(result: dict) -> dict:
    start_time = time.perf_counter()

    processed = {
        "retrieved_docs": [],
        "news_articles": [],
        "proprietary_data": result.get("proprietary_data", [])
    }

    # Collect all URLs to fetch
    tasks = []
    doc_map = {}

    # Process retriever docs
    for doc in result["retrieved_docs"]:
        url = doc["metadata"].get("source_url")
        starts_at = doc["metadata"].get("description", "")
        if url:
            task = asyncio.create_task(fetch_full_text_async(url, starts_at))
            tasks.append(task)
            doc_map[task] = ("retrieved_docs", doc)

    # Process Tavily news articles
    for article in result["news_articles"]:
        if is_specific_event(article):
            url = article["url"]
            starts_at = article["content"]
            task = asyncio.create_task(fetch_full_text_async(url, starts_at))
            tasks.append(task)
            doc_map[task] = ("news_articles", article)

    # Run all tasks concurrently
    fetch_start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    fetch_end = time.perf_counter()
    print(f"[INFO] Fetched {len(tasks)} URLs in {fetch_end - fetch_start:.2f} seconds")

    # Assign results back
    for task, full_text in zip(doc_map.keys(), results):
        target, item = doc_map[task]
        if target == "retrieved_docs":
            # append to original page_content in case article content isn't good
            item["page_content"] += "\n" + full_text
            processed["retrieved_docs"].append(item)
        else:
            item["content"] = full_text
            processed["news_articles"].append(item)

    total_time = time.perf_counter() - start_time
    print(f"[INFO] Finished process_result_async in {total_time:.2f} seconds")
    return processed