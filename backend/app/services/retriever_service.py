from datetime import datetime
import json
from app.models.tool_model import RetrieverInput
from app.config.settings import PROPRIETARY_VECTOR_STORE, PUBLIC_VECTOR_STORE

def public_retriever(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return []

    args = RetrieverInput(**args)

    query = args.query
    start_date = args.start_date
    end_date = args.end_date
    industries = args.industries
    region = args.region

    filters = {}
    print(f"[DEBUG retriever] query={query}, start_date={start_date}, end_date={end_date}, industries={industries}")
    if start_date or end_date:
        filters["event_date"] = {}
        if start_date:
            filters["event_date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            filters["event_date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")

    if industries:
        filters["affected_industry"] = {"$in": industries}

    if region:
        filters["Region"] = region

    docs = PUBLIC_VECTOR_STORE.similarity_search(
        query=query,
        k=5,
        pre_filter=filters
    )

    results = [{"metadata": doc.metadata, "page_content": doc.page_content} for doc in docs]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return results

def proprietary_retriever(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return []

    args = RetrieverInput(**args)

    query = args.query
    start_date = args.start_date
    end_date = args.end_date
    industries = args.industries
    region = args.region

    filters = {}
    print(f"[DEBUG proprietary_retriever] query={query}, start_date={start_date}, end_date={end_date}, industries={industries}")
    if start_date or end_date:
        filters["Incident Date"] = {}
        if start_date:
            filters["Incident Date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            filters["Incident Date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")

    if industries:
        filters["Industry"] = {"$in": industries}

    if region:
        filters["Region"] = region

    docs = PROPRIETARY_VECTOR_STORE.similarity_search(
        query=query,
        k=5,
        pre_filter=filters
    )

    results = [{"metadata": doc.metadata, "page_content": doc.page_content} for doc in docs]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return results