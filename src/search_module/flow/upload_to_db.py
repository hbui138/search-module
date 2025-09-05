import json
from pathlib import Path

from data_process_module.corpus_transform import flatten

from ..db.elastic import Elastic
from ..db.qdrant import Qdrant
from ..jina_client import Jina

embedded_corpus_data = json.loads(Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded_combined.json").read_text(encoding="utf-8"))
normal_corpus_data = json.loads(Path(r"d:\Work\VLSP\Dataset\legal_corpus.json").read_text(encoding="utf-8"))
flattened_data = flatten(normal_corpus_data)

qdrant = Qdrant()
elastic = Elastic()
jina = Jina()

db_name = "legal_corpus"

batch_size = 32
total = len(embedded_corpus_data)
print(f"Total items to upload: {total}")

for start in range(0, total, batch_size):
    end = min(start + batch_size, total)
    batch = embedded_corpus_data[start:end]

    qdrant.bulk_upload(db_name, batch)
    print(f"Qdrant upload done for items {start} to {end-1}.")

for start in range(0, total, batch_size):
    end = min(start + batch_size, total)
    batch = normal_corpus_data[start:end]

    elastic.bulk_upload(db_name, batch)
    print(f"Elastic upload done for items {start} to {end-1}.")