import json
import os

from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, questions_path, processed_path, ground_truths_path=None):
        with open(questions_path, 'r') as f:
            questions = json.load(f)["questions"]
        
        if ground_truths_path != None:
            with open(ground_truths_path, 'r') as f:
                ground_truths = json.load(f)["ground_truths"]
            for question, ground_truth in zip(questions, ground_truths):
                assert question["qid"] == ground_truth["qid"]
                question["retrieve"] = ground_truth["retrieve"]
        
        self.data = questions
        
        with open(os.path.join(processed_path, 'faq.json'), 'r') as f:
            self.source_faq = json.load(f)
        
    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        sample = self.data[index]
        category = sample["category"]
        source_id = sample["source"]
        
        source_context = []
        summary_context = []
        if category != "faq":
            base_path = os.path.join("Data", "dataPreprocessing", category)

            for id in source_id:
                file_path = os.path.join(base_path, f"{id}_text.txt")
                summary_file_path = os.path.join(base_path, f"{id}_text_summary.txt")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        source_context.append(text)
                except FileNotFoundError:
                    print(f"檔案 {file_path} 不存在，跳過此檔案。")
                except Exception as e:
                    print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
                
                try:
                    with open(summary_file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        summary_context.append(text)
                except FileNotFoundError:
                    print(f"檔案 {summary_file_path} 不存在，跳過此檔案。")
                except Exception as e:
                    print(f"讀取檔案 {summary_file_path} 時發生錯誤: {e}")
        else:
            for id in source_id:
                context = self.source_faq.get(str(id), "")
                source_context.append(context)

        sample["source_context"] = source_context
        sample["source_summary_context"] = summary_context
        return sample
    
if __name__ == "__main__":
    questions_path = 'Data/dataset/preliminary/questions_example.json'
    ground_truths_path = 'Data/dataset/preliminary/ground_truths_example.json'
    processed_path = 'Data/reference/processed'

    dataset = MyDataset(questions_path, ground_truths_path, processed_path)

    print(dataset[102])

    # 檢查是否有空的 context
    with open(os.path.join(processed_path, 'faq.json'), 'r') as f:
        source_faq = json.load(f)

    with open(os.path.join(processed_path, 'finance.json'), 'r') as f:
        source_finance = json.load(f)
    
    with open(os.path.join(processed_path, 'insurance.json'), 'r') as f:
        source_insurance = json.load(f)

    faq = []
    for key, value in source_faq.items():
        if value == "":
            faq.append(key)

    finance = []
    for key, value in source_finance.items():
        if value == "":
            finance.append(key)
    
    insurance = []
    for key, value in source_insurance.items():
        if value == "":
            insurance.append(key)
    
    print("faq no context: ", faq)
    print("finance no context: ", finance)
    print("insurance no context: ", insurance)
