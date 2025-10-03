from app.models.query_model import IncidentRequest, IncidentResponse
from app.models.pipeline_model import PipelineState
from app.services.extract_service import extract_query_params
from app.config.settings import llm
from app.services.evaluation_service import process_articles_with_dual_evaluation
from app.services.process_service import process_result_async
from app.services.retriever_service import proprietary_retriever, public_retriever
from app.services.summarisation_service import process_all_articles_flat
from app.services.tavily_service import tavily_search
from langgraph.graph import StateGraph, START, END

def extract_node(state: dict):
    """Extract keywords and optionally date range from user query"""
    query = state["query"]
    industries = state.get("industries", [])
    params = extract_query_params(llm, query)

    return {
        "keywords": params["keywords"],
        "start_date": params.get("start_date"),
        "end_date": params.get("end_date"),
        "industries": industries,
    }

def retriever_node(state: dict):
    """Retrieve relevant incidents from internal public database"""
    docs = public_retriever({
        "query": state["keywords"],
        "start_date": state["start_date"],
        "end_date": state["end_date"],
        "industries": state["industries"],
        "region": state["region"]
    })
    return {"retrieved_docs": docs}

def proprietary_node(state: dict):
    """Retrieve relevant incidents from proprietary claims database"""
    docs = proprietary_retriever({
        "query": state["keywords"],
        "start_date": state["start_date"],
        "end_date": state["end_date"],
        "industries": state["industries"],
        "region": state["region"]
    })
    return {"proprietary_data": docs}

def tavily_node(state: dict):
    """Run Tavily web search for news articles"""
    articles = tavily_search({
        "query": state["keywords"],
        "start_date": state["start_date"],
        "end_date": state["end_date"],
        "industries": state["industries"],
    })
    return {"news_articles": articles}

async def process_node(state: dict):
    """Remove generic articles, fetch and clean content from source_url asynchronously"""
    processed = await process_result_async({
        "retrieved_docs": state["retrieved_docs"],
        "news_articles": state["news_articles"],
        "proprietary_data": state["proprietary_data"]
    })
    return {
        "retrieved_docs": processed["retrieved_docs"],
        "news_articles": processed["news_articles"],
        "proprietary_data": processed["proprietary_data"]
    }

async def summarise_node(state: dict):
    """Summarise all articles in parallel"""
    articles_dict = {
        "retrieved_docs": state["retrieved_docs"],
        "news_articles": state["news_articles"],
        "proprietary_data": state["proprietary_data"]
    }
    processed = await process_all_articles_flat(articles_dict)
    return {"processed_articles": processed}

async def evaluate_node(state: dict):
    """Run dual evaluation (hallucination + summarisation quality)"""
    evaluated = await process_articles_with_dual_evaluation(state["processed_articles"])
    return {"evaluated_articles": evaluated}

# --- Build the graph ---
workflow = StateGraph(PipelineState)

# Add nodes
workflow.add_node("extract", extract_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("proprietary", proprietary_node)
workflow.add_node("tavily", tavily_node)
workflow.add_node("process", process_node)
workflow.add_node("summarise", summarise_node)
workflow.add_node("evaluate", evaluate_node)

# Add edges
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retriever")
workflow.add_edge("extract", "proprietary")
workflow.add_edge("extract", "tavily")
workflow.add_edge("retriever", "process")
workflow.add_edge("tavily", "process")
workflow.add_edge("proprietary", "process")
workflow.add_edge("process", "summarise")
workflow.add_edge("summarise", "evaluate")
workflow.add_edge("evaluate", END)

graph = workflow.compile()

async def run_graph(request: IncidentRequest) -> IncidentResponse:
    results = await graph.ainvoke({
        "query": request.query,
        "industries": request.industries,
        "region": request.region
    })

    return IncidentResponse(
        query=results["query"],
        industries=results.get("industries"),
        region=results.get("region"),
        evaluated_articles=results.get("evaluated_articles")
    )