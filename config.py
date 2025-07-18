import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Azure OpenAI configuration
AZURE_ENDPOINT_URL = os.getenv("AZURE_ENDPOINT_URL", "azure")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "o3")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-08-01-preview")

# Initialize Async OpenAI client
gpt_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT_URL,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_API_VERSION,
)
