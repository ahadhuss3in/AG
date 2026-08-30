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
    try:
        model= GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2-preview",
            google_api_key=config.GEMINI_API_KEY,
        )
        model.embed_query("test")
        logfire.info(f"Gemini Embeddings are ready. Model used {model.model}")
        return model
    except Exception as e:
        logfire.warning(f"Gemini probe failed : {e}. Will use the sentence-transfromer as fallback model")
        return None

def load_fallback():
    from sentence_transformers import SentenceTransformer
    logfire.info("Loading fallback sentence transformer(768 DIM)")
    return SentenceTransformer("all-mpnet-base0v2")

def _init():
    global _active_model, _model_type

    if _active_model is not None:
        return _active_model, _model_type   

    gemini = _probe_gemini()
    if gemini:
        _active_model = gemini 
        _model_type = "gemini"
    else :
         _active_model = load_fallback() 
         _model_type = "Sentence-Transformer-fallback"

    return

def get_embedding_dim() -> int:
    """returns the vec dim fir active model."""
    return _GEMINI_DIM if _model_type=="gemini" else _FALLBACK_DIM

def embedding_batch(batch:list[str]) -> list[list[float]]:
    """embedding a batch using the embedding model"""
    if _model_type == "gemini":
        for r in range (5):
            try:
                ## actual embedding process which is ran
                return _active_model.embed_documents(batch)
            ## rate limit error handling based on no of retries
            except Exception as e:
                err = str(e).lower()
                ## free tier so checking for rate limiting
                rate_limited_check = any(x in err for x in ("429", "quota","rate","resource_exhausted","billing","exceeded"))
                if rate_limited_check and r!=4:
                    sleep = 2**r
                    logfire.warning(
                        f"Gemini is getting rate limited:Retrying in {sleep} seconds "
                        f"Attempts left {r+1}/5."
                    )
                else :
                    logfire.error(f"Gemini Embedding failed:{e}")
                    raise 
        raise RuntimeError("Gemini embedding failed after 5 exponential retries.")
    else:
        return _active_model.encode(batch, show_progress_bar=False).tolist()



## aha now the query should also be in same format as asnwer right?
##so will also embedd the query so u can compare apple to apple in hdhahduh(perosnal work for embeddings) language

def embedding_query(query:str) -> list[float]:
    """embedded query to compare"""
    return 

def embedded_texts(texts:list[str])-> list[list[float]]: 
    _init()