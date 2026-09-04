import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import config
from  services.Rag.embedding.embeddings import embedding_query


# Initialize Qdrant Client
client = QdrantClient(
    url=config.QDRANT_CLUSTER_ENDPOINT,
    api_key=config.QDRANT_API_KEY
)

def search_enterprise_knowledge(query: str, limit: int = 8):
    """
    Performs a high-precision search in the enterprise knowledge base.
    """
    try:
        query_vector = embedding_query(query)

        # Using query_points 
        response = client.query_points(
            collection_name=config.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            with_payload=True # JSON
        )

        results = []
        for res in response.points:
            results.append({
                "content": res.payload.get("text", ""),
                "source": res.payload.get("source", "Unknown"),
                "score": res.score
            })
        
        return results
    except Exception as e:
        logfire.error(f" Qdrant Search Failed: {e}")
        return []