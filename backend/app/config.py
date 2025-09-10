# this file is backend/app/config.py
'''
Central place to create and share a single MongoDB client and a handle to your database.
'''
import os
from dotenv import load_dotenv
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

## Load environment variables from parent directory
# from cur file go up to its parent 3 times to NuSxMarsh folder
parent_dir = Path(__file__).resolve().parent.parent.parent 
# then go to the .env file
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Now you can access the MONGO_URL
MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
# database name
db = client["DB"]