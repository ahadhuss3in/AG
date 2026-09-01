import os 
from dotenv import load_dotenv

load_dotenv()


class config:
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_CLUSTER_ENDPOINT = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    QDRANT_COLLECTION = "RAGAAAAA"
    # which embedding provider to try first: "gemini" or "custom".
    # "custom" means any openai-compatible embeddings endpoint, not just
    # openrouter, configured entirely by the four settings below. either
    # way, the local sentence-transformer is still the fallback if the
    # chosen one fails.
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    CUSTOM_EMBEDDING_BASE_URL = os.getenv("CUSTOM_EMBEDDING_BASE_URL")
    CUSTOM_EMBEDDING_API_KEY = os.getenv("CUSTOM_EMBEDDING_API_KEY")
    CUSTOM_EMBEDDING_MODEL = os.getenv("CUSTOM_EMBEDDING_MODEL")
    # max characters sent per chunk to the custom model. also used to size
    # chunk_text() up front, since a custom model's real token limit is
    # unknown ahead of time and varies per model.
    CUSTOM_EMBEDDING_MAX_CHARS = int(os.getenv("CUSTOM_EMBEDDING_MAX_CHARS", "900"))
    MODEL="openrouter/free"


config = config()
