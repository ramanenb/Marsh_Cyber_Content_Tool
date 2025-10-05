from fastapi import APIRouter, UploadFile, File, HTTPException
from collections import defaultdict
from app.config.settings import DB
from datetime import datetime
import pandas as pd
import traceback
from io import BytesIO
from app.services.prop_data_processing_service import marsh_data_process, upsert_mongo

router = APIRouter()

@router.post("/upload_prop_data/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".xlsx"):
            contents = await file.read()  # Read file bytes
            df = pd.read_excel(BytesIO(contents))
            marsh_data_processed = marsh_data_process(df)
            upsert_mongo(marsh_data_processed)
            return {"status": "success", "rows": len(df)}
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
