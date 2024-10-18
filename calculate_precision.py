import json
import argparse

def calculate_precision(y_true, y_pred):
    if len(y_true) != len(y_pred):
        raise ValueError("Length of ground truths and predictions do not match!")

    total = 0
    for true, pred in zip(y_true, y_pred):
        if true["qid"] != pred["qid"]:
            raise ValueError(f"QID mismatch: ground truth qid={true['qid']}, prediction qid={pred['qid']}")
        else:
            total += true["retrieve"] == pred["retrieve"]

    return total / len(y_true)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--ground_truth_path', type=str, required=True, help='讀取答案檔案路徑')
    parser.add_argument('--prediction_path', type=str, required=True, help='讀取預測答案檔案路徑')

    args = parser.parse_args()

    with open(args.ground_truth_path, 'r') as f:
        data = json.load(f)
    y_true = data['ground_truths']

    with open(args.prediction_path, 'r') as f:
        data = json.load(f)
    y_pred = data['answers']
    
    print(calculate_precision(y_true, y_pred))
