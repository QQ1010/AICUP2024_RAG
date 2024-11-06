import json
import argparse

def calculate_precision(y_true, y_pred):
    if len(y_true) != len(y_pred):
        raise ValueError("Length of ground truths and predictions do not match!")

    correct = 0
    finance_false_cases = []
    insurance_false_cases = []
    faq_false_cases = []
    for true, pred in zip(y_true, y_pred):
        if true["qid"] != pred["qid"]:
            raise ValueError(f"QID mismatch: ground truth qid={true['qid']}, prediction qid={pred['qid']}")
        else:
            if true["retrieve"] == pred["retrieve"]:
                correct += 1
            else:
                if true["category"] == "finance":
                    finance_false_cases.append((true, pred))
                elif true["category"] == "insurance":
                    insurance_false_cases.append((true, pred))
                elif true["category"] == "faq":
                    faq_false_cases.append((true, pred))
    print("correct: ", correct)
    print("total: ", len(y_true))
    print("finance_false_cases: ", len(finance_false_cases))
    print("insurance_false_cases: ", len(insurance_false_cases))
    print("faq_false_cases: ", len(faq_false_cases))
    print("finance_false_cases: ", finance_false_cases)
    print("insurance_false_cases: ", insurance_false_cases)
    print("faq_false_cases: ", faq_false_cases)
    return correct / len(y_true)

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
