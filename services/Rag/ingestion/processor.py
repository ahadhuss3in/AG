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
    with logfire.span("Processing File", file=filename, sourcetype=str):
        try:
            ext= filename.lower().rsplit(".",1)[-1]
            if ext == "pdf":
                doc = loadpdf(file_path)
            elif ext in ("html", "htm"):
                doc = loadhtml(file_path)
            elif ext in ("docx", "pptx"):
                doc = loadoffice(file_path)
            elif ext == "txt":
                doc = loadtext(file_path)
            else:
                logfire.warning(
                    "unsupported file extension, skipping this file",
                    file=filename,
                    ext=ext,
                )
                return
            if not doc or not doc.strip():
                logfire.warning(f"File {filename} has no extractable content, skipping it.")
                return

            
            ## chunk the text now 
            chunks=chunk_text(doc)
            if not chunks:
                return
            
            #saved processed metadata locall
            processed_data={
                "filename":filename,
                "sourcetype":sourcetype,
                "chunks":chunks,
            }
            local_path = saved_prog_local(processed_data,sourcetype,filename)
            logfire.info(f"saved process data -> {local_path}")
            with logfire.span("Vectorizing and Indexing"):
                embeddings = embedded_texts(chunks)
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "text":chunk,
                            "source":filename,
                            "sourcetype":sourcetype,

                        },
                    )

                    #using zip to pair up the chunk and vector to each other chunks[1]->embeddigs[1]
                    for chunk,vector in zip(chunks,embeddings)
                        
                ]

                q_cliient.upsert(
                    collection_name=config.QDRANT_COLLECTION,
                    points=points,    
                )
                logfire.info(f"indexed {len(points)} points to Qdrant from {filename}.")
        except Exception as e:
            # one bad file should not stop the whole ingestion run. so we log it and return error
            
            logfire.error(
                f"failed to process this file{filename}:{e}"
            )
        

def process_dir(dir_path:str, sourcetype:str):
    """Process every file inside one directory, under one sourcetype."""
    with logfire.span("Scanning directory",path=dir_path,sourcetype=sourcetype):
        files=[f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path,f))]
        logfire.info(f"Found {len(files)} files in {dir_path}. ")

        for filename in files:
            file_path = os.path.join(dir_path, filename)
            process_file(file_path, filename, sourcetype)


def run_all_ingestion(base_dir:str, explicit_source_type:str = None, wipe:bool=False):
    """
    scane the dir, map sub folder to source rypes and ingest all avail documents.
    pass --wipe to drop and recreate the qdrant collection b4 ingestion
    """
    if wipe and q_cliient.collection_exists(config.QDRANT_COLLECTION):
        q_cliient.delete_collection(config.QDRANT_COLLECTION)
        logfire.info(f"wiped existing collection {config.QDRANT_COLLECTION}")

    if not q_cliient.collection_exists(config.QDRANT_COLLECTION):
        dim = get_embedding_dim()
        q_cliient.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=dim,
                distance=models.Distance.COSINE,
            ),
        )
        logfire.info(
                        f"created collection {config.QDRANT_COLLECTION} "
                        f"({dim}-dim, Cosine Comparison method)"
                    )

    # this runs every time, not just when the collection was just created
    subdirs=[
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir,d))
    ]

    if not subdirs:
        if explicit_source_type:
            sourcetype=explicit_source_type
        else:
            basename=os.path.basename(os.path.normpath(base_dir)).lower()
            sourcetype = (
                "true" if "true" in basename
                else "noisy" if "noisy" in basename
                else "general"
            )
        process_dir(base_dir, sourcetype)
    else:
        for sub in subdirs:
            process_dir(os.path.join(base_dir, sub), sub)