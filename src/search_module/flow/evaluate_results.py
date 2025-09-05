import json
from pathlib import Path
from typing import List, Dict


def load_json(file_path: str) -> list:
	"""Load data from a JSON file."""
	try:
		data = json.loads(Path(file_path).read_text(encoding="utf-8"))
		return data
	except Exception as e:
		print(f"Error loading data from {file_path}: {e}")
		return []


def detailed_match_info(data_path: str, results_path: str) -> List[Dict]:
	"""
	For each query, return:
	- number of correctly retrieved laws
	- total number of relevant laws
	- total number of retrieved laws
	"""
	ground_truth = load_json(data_path)
	results = load_json(results_path)
	gt_dict = {entry["qid"]: set(entry["relevant_laws"]) for entry in ground_truth}
	detailed_info = []

	for res in results:
		qid = res["qid"]
		predicted = set(res.get("relevant_laws", []))
		actual = gt_dict.get(qid, set())

		correct = predicted & actual
		detailed_info.append({
			"qid": qid,
			"correct_retrieved": len(correct),
			"total_relevant": len(actual),
			"total_retrieved": len(predicted)
		})

	return detailed_info


def calculate_metrics(data_path: str, results_path: str) -> Dict[str, float]:
	"""
	Calculate average Precision, Recall, and F2-measure.

	Precision = avg(correct / retrieved)
	Recall = avg(correct / relevant)
	F2 = (5 * P * R) / (4 * P + R)
	"""
	detailed_info = detailed_match_info(data_path, results_path)
	precision_list = []
	recall_list = []

	for entry in detailed_info:
		correct = entry["correct_retrieved"]
		retrieved = entry["total_retrieved"]
		relevant = entry["total_relevant"]

		precision = correct / retrieved if retrieved > 0 else 0.0
		recall = correct / relevant if relevant > 0 else 0.0

		precision_list.append(precision)
		recall_list.append(recall)

	avg_precision = sum(precision_list) / len(precision_list) if precision_list else 0.0
	avg_recall = sum(recall_list) / len(recall_list) if recall_list else 0.0

	if avg_precision + avg_recall == 0:
		f2 = 0.0
	else:
		f2 = (5 * avg_precision * avg_recall) / (4 * avg_precision + avg_recall)

	return {
		"precision": avg_precision,
		"recall": avg_recall,
		"f2": f2
	}


# --- Example Usage ---
if __name__ == "__main__":
	data_path = r"d:\Work\VLSP\Dataset\train.json"
	results_path = r"d:\Work\VLSP\Dataset\train_results.json"

	results_info = detailed_match_info(data_path, results_path)

	for entry in results_info:
		print(f"QID: {entry['qid']}")
		print(f"  Correctly Retrieved: {entry['correct_retrieved']}")
		print(f"  Total Relevant Laws: {entry['total_relevant']}")
		print(f"  Total Retrieved Laws: {entry['total_retrieved']}")
		print("-" * 40)

	metrics = calculate_metrics(data_path, results_path)
	print("=== Overall Metrics ===")
	print(f"Precision: {metrics['precision']:.4f}")
	print(f"Recall:    {metrics['recall']:.4f}")
	print(f"F2-score:  {metrics['f2']:.4f}")
