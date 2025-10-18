from fastapi import APIRouter, UploadFile, File, HTTPException
from collections import defaultdict
from app.config.settings import DB, PROPRIETARY_COLLECTION
from datetime import datetime
import pandas as pd
import traceback
from io import BytesIO
from bson.json_util import dumps
import json
from math import isnan
from bson import json_util, ObjectId
from app.services.prop_data_processing_service import marsh_data_process, upsert_mongo, save_to_s3_bytes, list_files_with_urls

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

        def normalize(doc):
            for k, v in doc.items():
                # Handle ObjectId
                if isinstance(v, ObjectId):
                    doc[k] = str(v)
                # Handle datetime
                elif isinstance(v, datetime):
                    doc[k] = v.isoformat()+'Z'
                # Handle float('nan')
                elif isinstance(v, float) and isnan(v):
                    doc[k] = None
                # Handle nested MongoDB extended JSON
                elif isinstance(v, dict):
                    if "$numberDouble" in v:
                        val = float(v["$numberDouble"])
                        doc[k] = None if isnan(val) else val
                    elif "$numberInt" in v:
                        doc[k] = int(v["$numberInt"])
                    elif "$date" in v:
                        doc[k] = v["$date"]
                    else:
                        normalize(v)
            return doc
        
        #json_data = json.loads(dumps(data))
        normalized_data = [normalize(d) for d in data]

        return {"status": "success", "data": normalized_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/list_uploaded_files/")
async def list_uploaded_files():
    try:
        files = list_files_with_urls()
        return {"status": "success", "data": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.post("/check_duplicates/")
async def check_duplicates(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".xlsx"):
            contents = await file.read()  # Read file bytes
            df = pd.read_excel(BytesIO(contents))

            if "Claim Number" not in df.columns:
                raise HTTPException(status_code=400, detail="Missing 'Claim Number' column")

            claim_numbers = df["Claim Number"].dropna().astype(str).tolist()

            existing_claims = PROPRIETARY_COLLECTION.find(
                {"_id": {"$in": claim_numbers}},
                {"_id": 1}
            )

            duplicates = [doc["_id"] for doc in existing_claims]
            return {"status": "success", "duplicates": duplicates}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

