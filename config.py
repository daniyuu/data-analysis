import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Server configuration
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

# Azure OpenAI configuration
AZURE_ENDPOINT_URL = os.getenv("AZURE_ENDPOINT_URL", "azure")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "o3")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-08-01-preview")

# Data
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(CURRENT_DIR, "data"))
REPORT_DIR = os.path.join(DATA_DIR, "reports")

# Initialize Async OpenAI client
gpt_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT_URL,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_API_VERSION,
)
