# this file is backend/app/config.py
'''
Central place to create and share a single MongoDB client and a handle to your database.
'''
import os
from dotenv import load_dotenv
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

## Load environment variables from /backend/.env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# MongoDB settings
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL) # Used for non-blocking database operations e.g. dashboard
pymongo_client = MongoClient(MONGO_URL) # Used for retrieval

# Database and collections 
DB_NAME = "DB"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"
PUBLIC_COLLECTION_NAME = "europec_maryland_test"
PROPRIETARY_COLLECTION_NAME = "marsh_proprietary_data"
INDUSTRIES_COLLECTION_NAME = "industries"

DB = client[DB_NAME]
PUBLIC_COLLECTION = pymongo_client[DB_NAME][PUBLIC_COLLECTION_NAME]
PROPRIETARY_COLLECTION = pymongo_client[DB_NAME][PROPRIETARY_COLLECTION_NAME]
INDUSTRIES_COLLECTION = pymongo_client[DB_NAME][INDUSTRIES_COLLECTION_NAME]

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model configuration
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Vector stores
PUBLIC_VECTOR_STORE = MongoDBAtlasVectorSearch(
    collection=PUBLIC_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
    embedding_key="vector_embedding",
    text_key="embedding_text"
)

PROPRIETARY_VECTOR_STORE = MongoDBAtlasVectorSearch(
    collection=PROPRIETARY_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
    embedding_key="vector_embedding",
    text_key="embedding_text"
)