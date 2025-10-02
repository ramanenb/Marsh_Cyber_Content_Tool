from typing import List
from app.config.settings import DB

async def get_industry_list() -> List[str]:
    cursor = DB["industries"].find({}, {"_id": 0, "industry": 1})
    return [doc["industry"] async for doc in cursor]