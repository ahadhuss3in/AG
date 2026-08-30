import time
import logfire 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import config

BATCH_SIZE = 50 
_GEMINI_DIM = 3072  #Dimention of embedding model ( it just means it has these many elements)
_FALLBACK_DIM = 768 

_active_model = None
_model_type : str | None = None #gemini or fallback

def _probe_gemini():
    """a embedded call to verify gemini is running 
    please use my other project which is a AI gateway to avoid this :)
    """

def load_fallback():
    return

def _init():
    return

def get_embedding_dim() -> int:
    """returns the vec dim fir active model."""
    return

def embedding_batch(batch:list[str]) -> list[list[float]]:
    """embedding a batch using the embedding model"""
    return 


## aha now the query should also be in same format as asnwer right?
##so will also embedd the query so u can compare apple to apple in hdhahduh(perosnal work for embeddings) language

def embedding_query(query:str) -> list[float]:
    """embedded query to compare"""
    return 

def embedded_texts(texts:list[str])-> list[list[float]]: 
    _init()