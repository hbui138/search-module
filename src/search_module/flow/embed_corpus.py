import json
from pathlib import Path

from data_process_module.corpus_transform import flatten
from ..jina_client import Jina

corpus_data = json.loads(Path(r"d:\Work\VLSP\Dataset\legal_corpus.json").read_text(encoding="utf-8"))
flattened_data = flatten(corpus_data)
jina = Jina()

batch_size = 32
total = len(flattened_data)

output_path = Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded_combined.json")
output_path_to_embed = Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded.json")

# Load already embedded data if exists
embedded_aids = set()
embedded_data = []
if output_path.exists():
    with output_path.open("r", encoding="utf-8") as f:
        embedded_data = json.load(f)
        embedded_aids = {item["aid"] for item in embedded_data if "aid" in item}
    print(f"Loaded {len(embedded_data)} already embedded entries.")

# Only embed new entries
to_embed = [item for item in flattened_data if item.get("aid") not in embedded_aids]
print(f"{len(to_embed)} entries left to embed.")

all_new_embedded = []

for start in range(0, len(to_embed), batch_size):
    end = min(start + batch_size, len(to_embed))
    batch = to_embed[start:end]

    print(f"Embedding batch from aid {batch[0]['aid']} to {batch[-1]['aid']}...")
    articles = [i["content_Article"] for i in batch]
    embeddings = jina.embed_by_batch(articles, batch_size=batch_size)
    print("Total embeddings received:", len(embeddings))
    print(f"Embedding complete for aid {batch[0]['aid']} to {batch[-1]['aid']}. Total embedded: {len(all_new_embedded)}")

    for i, data in enumerate(batch):
        data["embedding"] = embeddings[i]
        all_new_embedded.append(data)

    # Save progress every 1024 items or at the end
    if (len(all_new_embedded)) % 1024 == 0 or end == len(to_embed):
        print(f"Saving progress at {len(all_new_embedded)} embeddings...")
        with output_path_to_embed.open("w", encoding="utf-8") as f:
            json.dump(all_new_embedded, f, ensure_ascii=False, indent=2)

# Final save
with output_path_to_embed.open("w", encoding="utf-8") as f:
    json.dump(all_new_embedded, f, ensure_ascii=False, indent=2)

print(f"Saved embedded corpus to {output_path}")