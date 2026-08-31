import os 
import sys
import uuid
import json
import logfire

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import config
from services.Rag.retrieval.embeddings import embedded_texts, get_embedding_dim
from services.Rag.ingestion.loaders.pdf_loader import loadpdf
from services.Rag.ingestion.loaders.html_loader import loadhtml
from services.Rag.ingestion.loaders.office_loader import loadoffice
from services.Rag.ingestion.loaders.text_loader import loadtext
from services.Rag.ingestion.chuncking.splitter import chunk_text

logfire.configure(service_name="rag-ingestion-service")

PROCESSED_DATA_DIR = "ProcessedData"

## initialize qdrant 
q_cliient = QdrantClient(
    url = config.QDRANT_CLUSTER_ENDPOINT,
    api_key = config.QDRANT_API_KEY,
)

def saved_prog_local(data:dict, sourcetype:str, filename:str) -> str:
    """save the parsed chunk locall"""
    folder = os.path.join(PROCESSED_DATA_DIR, sourcetype)
    os.makeidrs(folder,exist_ok=True)
    dest= os.path.join(folder, f"{filename}.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False, indent=2)
    return dest 

def process_file(file_path:str, filename:str, sourcetype:str):
    """parse -> chunk -> save local -> embedd -> index in db"""
        

def process_dir(dir_path:str, sourcetype:str):
    """Porcess file in saved_file"""
    pass

def run_all_ingestion(base_dir:str, explicit_source_type:str = None, wipe:bool=False):
    """
    scane the dir, map sub folder to source rypes and ingest all avail documents.
    pass --wipe to drop and recreate the qdrant collection b4 ingestion
    """

