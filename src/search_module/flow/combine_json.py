import json
from pathlib import Path
from typing import Union

def combine_json_files(file1: Union[str, Path], file2: Union[str, Path], output_file: Union[str, Path]) -> None:
    # Read both JSON files
    with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Combine based on structure
    if isinstance(data1, list) and isinstance(data2, list):
        combined = data1 + data2
    elif isinstance(data1, dict) and isinstance(data2, dict):
        combined = {**data1, **data2}
    else:
        raise ValueError("JSON files do not have the same structure (both lists or both dicts).")

    # Write to output file
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(combined, out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    output_path_1 = Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded_combined.json")
    output_path_2 = Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded.json")
    output_file = Path(r"d:\Work\VLSP\Dataset\legal_corpus_embedded_combined.json")

    combine_json_files(output_path_1, output_path_2, output_file)
    print(f"Combined JSON files saved to {output_file} with {len(json.load(open(output_file, 'r', encoding='utf-8')))} entries.")