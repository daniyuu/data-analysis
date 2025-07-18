import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Azure OpenAI configuration
ENDPOINT_URL_Azure4oMini = os.getenv("AZURE_OPENAI_ENDPOINT_Azure4oMini", "azure")
DEPLOYMENT_NAME_Azure4oMini = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT_Azure4oMini", "gpt-4o-mini"
)
AZURE_OPENAI_API_KEY_Azure4oMini = os.getenv(
    "AZURE_OPENAI_API_KEY_Azure4oMini", "your-api-key"
)
API_VERSION_Azure4oMini = os.getenv(
    "AZURE_OPENAI_API_VERSION_Azure4oMini", "2024-08-01-preview"
)

# Initialize Async OpenAI client
gpt_client = AsyncAzureOpenAI(
    azure_endpoint=ENDPOINT_URL_Azure4oMini,
    api_key=AZURE_OPENAI_API_KEY_Azure4oMini,
    api_version=API_VERSION_Azure4oMini,
)
