import time 
import logfire
from flashrank import Ranker, RerankRequest

ranker= None

def get_ranker() -> Ranker:
    """
    Initialize the flashrank request engine
    ONNX model (ms-marco-MiniLM-L-6-v2) for ultra fast rerank

    """

    ## just initializing the ranker with a cache way 
    global ranker
    if ranker is None:
        logfire.info("Initializing cross-encoder for reranking")
        try :
            ranker = Ranker(cache_dir="/tmp/flashrank")
        except Exception:
            ranker = Ranker()
    return ranker


def rerank_documents(query:str, documents:list[str],top_n: int = 5) -> list[str]:
    """
    Re-ranking documnets using a crossencoder
    using a cross encoder since thiis is slow but produces accurate self attention / semantic
    relation between query
    flashrank uses the OnNx model quantized way locally
    """

    if not documents:
        return []

    start_time = time.time()
    logfire.info(f"Re-ranking sending {len(documents)} Documents for Re-Ranking")

    try:
        ranker = get_ranker()

       ## flashrank needs list of dict with id and text
        passages=[
            {"id": i, "text":doc}
            for i,doc in enumerate(documents)
        ]

        ## turn everything into a request obj ysing ReRankRequest
        request = RerankRequest(query=query, passages=passages)

        ##get the results
        results= ranker.rerank(request)

        reranked_docs = []
        ## from 0 to how much top_n results we need
        for res in results[:top_n]:
            reranked_docs.append(res['text'])

        ## time taken
        duration = time.time() - start_time
        top_score = results[0]['score'] if results else 'N/a'
        logfire.info (f"Reranking done in {duration:.3f} seconds. Top Semantic score: {top_score}.")

        return reranked_docs
    except Exception as e:
        logfire.error(f"ReRanker Semantic failed :{e}")
        ##3 fallbac and give result without reranking
        return documents[:top_n]

