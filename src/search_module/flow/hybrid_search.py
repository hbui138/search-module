import re
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from data_process_module.corpus_transform import flatten

from ..db.elastic import Elastic
from ..db.qdrant import Qdrant
from ..jina_client import Jina

def escape_query_string(query: str) -> str:
    return re.sub(r'([+\-!(){}[\]^"~*?:\\/])', r'\\\1', query)

# Initialize clients once (shared across threads)
elastic = Elastic()
qdrant = Qdrant()
jina = Jina()

db_name = "legal_corpus"

# Load queries
queries_path = r"d:\Work\VLSP\Dataset\train.json"
queries_data = json.loads(Path(queries_path).read_text(encoding="utf-8"))
queries = [{"qid": item["qid"], "question": item["question"]} for item in queries_data]
queries = queries[:50]  # For testing, limit to 50 items

print("Queries size:", len(queries))

# --- Define per-query logic ---
def process_query(query_obj):
    qid = query_obj["qid"]
    query = query_obj["question"]
    qdrant_results_list = []
    elastic_results_list = []

    # --- QDRANT ---
    try:
        qdrant_results = qdrant.client.search(
            collection_name=db_name,
            query_vector=jina.embed([query])[0],
            limit=3,
        )
    except Exception as e:
        print(f"[Qdrant Error] Query {qid}: {e}")
        qdrant_results = []

    for hit in qdrant_results:
        payload = hit.payload
        qdrant_results_list.append({
            "doc_id": payload.get("doc_id"),
            "law_id": payload.get("law_id"),
            "aid": payload.get("aid"),
            "content_Article": payload.get("content_Article")
        })

    # --- ELASTIC ---
    try:
        elastic_results = elastic.client.search(
            index=db_name,
            query={"query_string": {"query": escape_query_string(query)}}
        )
    except Exception as e:
        print(f"[Elastic Error] Query {qid}: {e}")
        elastic_results = {"hits": {"hits": []}}

    for hit in elastic_results["hits"]["hits"]:
        source = hit["_source"]
        elastic_results_list.append({
            "doc_id": source["doc_id"],
            "law_id": source["law_id"],
            "aid": source.get("aid"),
            "content_Article": source.get("content_Article")
        })

    # --- MERGE + DEDUPLICATE ---
    results_list = list({item["aid"]: item for item in (qdrant_results_list + elastic_results_list) if item.get("aid")}.values())

    if not results_list:
        return {"qid": qid, "relevant_laws": []}

    articles = [item["content_Article"] for item in results_list]
    try:
        rerank_results = jina.rerank(query, articles)
        reranked_list = [
            results_list[int(item["index"])] | {"relevance_score": item["relevance_score"]}
            for item in rerank_results
        ]
        reranked_aids = [item.get("aid") for item in reranked_list]
    except Exception as e:
        print(f"[Rerank Error] Query {qid}: {e}")
        reranked_aids = []

    print(f"[Done] Query {qid} | Top {len(reranked_aids)} aids: {reranked_aids}")
    return {"qid": qid, "relevant_laws": reranked_aids}

# --- Run in parallel ---
final_results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_query, q) for q in queries]
    for future in as_completed(futures):
        result = future.result()
        final_results.append(result)

# --- Save results ---
output_path = Path(r"d:\Work\VLSP\Dataset\train_results.json")
output_path.write_text(json.dumps(final_results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResults saved to: {output_path}")
