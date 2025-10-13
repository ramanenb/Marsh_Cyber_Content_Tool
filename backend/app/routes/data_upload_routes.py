from fastapi import APIRouter, UploadFile, File, HTTPException
from collections import defaultdict
from app.config.settings import DB, PROPRIETARY_COLLECTION
from datetime import datetime
import pandas as pd
import traceback
from io import BytesIO
from bson.json_util import dumps
import json
from app.services.prop_data_processing_service import marsh_data_process, upsert_mongo, save_to_s3_bytes

router = APIRouter()

@router.post("/upload_prop_data/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".xlsx"):
            contents = await file.read()  # Read file bytes
            s3_key = save_to_s3_bytes(contents, file.filename)
            df = pd.read_excel(BytesIO(contents))
            marsh_data_processed = marsh_data_process(df)
            upsert_mongo(marsh_data_processed)
            return {"status": "success", "rows": len(df), "s3_key": s3_key}
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_prop_data/")
async def get_prop_data():

    try:
        projection = {
            "_id": 1,
            "Coverage": 1,
            "Client Name": 1,
            "Incident Date": 1,
            "Brief Description of Incident": 1,
            "Lead Insurer": 1,
            "Total Paid": 1,
            "Policy Currency": 1,
            "CUR/USD": 1,
            "Total Paid (USD)": 1,
            "Claim Handler": 1,
            "Country (Set ID)": 1,
            "Cause": 1,
            "Type of Claim": 1,
            "Sub Type of Claim": 1,
            "Loss Details": 1,
            "Additional Loss Details": 1,
            "Remarks": 1,
            "Additional Long Remarks": 1,
            "Claims Handling Office": 1,
            "Claim Result": 1,
            "Claim Position": 1,
            "Industry": 1,
            "Marsh Loss Estimate (USD)": 1,
            "Date Reported to Insurer": 1,
            "Legal Fees": 1,
            "IT Forensic Fees": 1,
            "PR Fees": 1,
            "BI Loss": 1,
            "Ransom": 1,
            "Credit Monitoring": 1,
            "Fine": 1,
            "Third Party Liability": 1,
            "Region": 1
        }

        data = list(PROPRIETARY_COLLECTION.find({}, projection))     
        json_data = json.loads(dumps(data))

        return {"status": "success", "data": json_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}
