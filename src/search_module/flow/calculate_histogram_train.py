import json
from collections import Counter
from typing import Dict
import matplotlib.pyplot as plt

def histogram_of_relevant_laws_from_file(file_path: str = "train.json") -> Dict[int, int]:
    """
    Loads data from a JSON file and calculates a histogram of the number of relevant laws per question.

    Args:
        file_path: Path to the JSON file (default is "train.json").

    Returns:
        A dictionary mapping the number of laws to the number of questions having that count.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    counts = [len(item.get("relevant_laws", [])) for item in data]
    histogram = Counter(counts)
    return dict(histogram)

def plot_histogram(hist: Dict[int, int]) -> None:
    """
    Plots a histogram from the given frequency dictionary and adds count labels.

    Args:
        hist: A dictionary mapping number of laws to frequency of questions.
    """
    keys = sorted(hist.keys())
    values = [hist[k] for k in keys]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(keys, values, color='skyblue', edgecolor='black')

    plt.xlabel('Number of Relevant Laws per Question')
    plt.ylabel('Number of Questions')
    plt.title('Histogram of Relevant Laws per Question in Training Data')
    plt.xticks(keys)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{int(height)}', 
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

def get_qids_with_law_counts(data: list, counts: set) -> Dict[int, list]:
    """
    Returns qid lists for each target relevant_laws count.

    Args:
        data: List of question dictionaries.
        counts: Set of law counts to filter by.

    Returns:
        A dictionary mapping from relevant_laws count to list of qids.
    """
    result = {count: [] for count in counts}
    for item in data:
        num_laws = len(item.get("relevant_laws", []))
        if num_laws in counts:
            result[num_laws].append(item["qid"])
    return result

if __name__ == "__main__":
    train_data_path = r"d:\Work\VLSP\Dataset\train.json"
    
    # Load data
    with open(train_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Compute and plot histogram
    hist = histogram_of_relevant_laws_from_file(train_data_path)
    print("Histogram of relevant law counts:", hist)
    plot_histogram(hist)
    
    # Get and print qids with specific counts
    target_counts = {5, 6, 7, 8, 9}
    qid_groups = get_qids_with_law_counts(data, target_counts)

    for count in sorted(qid_groups):
        print(f"\nQuestions with {count} relevant laws:")
        for qid in qid_groups[count]:
            print(f"  - qid: {qid}")
