import time
import logfire 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import config

BATCH_SIZE = 50 
_GEMINI_DIM = 3072
_FALLBACK_DIM = 758

