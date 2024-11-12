import json
import os
from torch.utils.data import Dataset

class MyDataset(Dataset):
    """
    讀取訓練資料，轉存成 Dataset 類別
    """
    def __init__(self, questions_path, reference_path, ground_truths_path=None):
        self.source_faq = {}
        self.questions_path = questions_path
        self.reference_path = reference_path

        # 讀取問題資料
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions = json.load(f).get("questions", [])
        self.data = questions

        # 讀取 FAQ 資料
        faq_path = os.path.join(reference_path, 'faq.json')
        if os.path.isfile(faq_path):
            with open(faq_path, 'r', encoding='utf-8') as f:
                self.source_faq = {str(key): value for key, value in json.load(f).items()}
        else:
            print(f"Error: FAQ file '{faq_path}' not found.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index, is_use_summary='False'):
        if index < 0 or index >= len(self.data):
            raise IndexError("Index out of range")

        sample = self.data[index]
        category = sample["category"]
        source_id = sample["source"]

        source_context = []
        summary_context = []

        if category != "faq":
            base_path = os.path.join(self.reference_path, category)

            for id in source_id:
                file_path = os.path.join(base_path, f"{id}_text.txt")
                summary_file_path = os.path.join(base_path, f"{id}_text_summary.txt")
                
                # 讀取主檔案
                text = self.read_file(file_path)
                if text:
                    source_context.append(text)
                if is_use_summary == 'True':
                    # 讀取摘要檔案
                    summary_text = self.read_file(summary_file_path)
                    if summary_text:
                        summary_context.append(summary_text)
        else:
            # 處理 FAQ 類別
            for id in source_id:
                context = self.source_faq.get(str(id), "")
                source_context.append(context)

        sample["source_context"] = source_context
        if is_use_summary == 'True':
            sample["source_summary_context"] = summary_context
        
        return sample

    def read_file(self, file_path):
        """ 讀取檔案內容並處理錯誤 """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"檔案 {file_path} 不存在，跳過此檔案。")
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
        return None