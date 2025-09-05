import json
from pathlib import Path

from data_process_module.corpus_transform import flatten

corpus_data = json.loads(Path("VLSP\Dataset\legal_corpus.json").read_text(encoding="utf-8"))
flattened_data = flatten(corpus_data)

output_path = Path("flattened_data.json")
output_path.write_text(json.dumps(flattened_data, ensure_ascii=False, indent=4), encoding="utf-8")