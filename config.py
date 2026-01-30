import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # Supports "openai", "deepseek", "gemini" etc if using compatible endpoints
    AI_PROVIDER_BASE_URL = os.getenv("AI_PROVIDER_BASE_URL", "https://api.openai.com/v1") 
    AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-4o")

    # Google Sheets
    GOOGLE_CREDENTIALS_FILE = "credentials.json"
    
    # Crawler
    MAX_CONCURRENT_CRAWLS = 1
    USER_AGENT = "ShoCial-Vendor-Import-Bot/1.0"
