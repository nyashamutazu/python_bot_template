import os 
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = int(os.getenv("ACCOUNT_ID"))
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")
ACCOUNT_SERVER = os.getenv("ACCOUNT_SERVER")
        
