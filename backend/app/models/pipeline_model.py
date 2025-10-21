from typing import List, Optional, TypedDict

class PipelineState(TypedDict):
    query: str
    industries: List[str]
    region: str
    keywords: str
    start_date: Optional[str]
    end_date: Optional[str]
    retrieved_docs: List
    news_articles: List
    proprietary_data: List
    processed_articles: List
    evaluated_articles: List