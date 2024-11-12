import os
import json
import argparse
from tqdm import tqdm

def process_faq_data(source_path, output_path):
    """
    處理 FAQ 資料，將問題和答案合併成一個 JSON 檔案。
    """
    # 檢查來源檔案是否存在
    if not os.path.isfile(source_path):
        print(f"Error: Source file '{source_path}' does not exist.")
        return

    corpus_dict_faq = {}
    
    try:
        # 讀取來源 JSON 檔案
        with open(source_path, 'r', encoding='utf-8') as f:
            key_to_source_dict = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{source_path}': {e}")
        return

    # 處理 FAQ 資料
    for key, value in tqdm(key_to_source_dict.items(), total=len(key_to_source_dict)):
        content = ''.join([item['question'] + '、'.join(item['answers']) for item in value])
        corpus_dict_faq[key] = content

    # 排序 FAQ 字典
    sorted_corpus_dict_faq = dict(sorted(corpus_dict_faq.items(), key=lambda x: int(x[0])))

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_corpus_dict_faq, f, ensure_ascii=False, indent=4)
        print(f"Successfully written to '{output_path}'.")
    except Exception as e:
        print(f"Error writing file '{output_path}': {e}")
        return

    return sorted_corpus_dict_faq

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process FAQ JSON data.')
    parser.add_argument('--source_path', type=str, required=True, help='讀取 JSON 檔案參考資料路徑')
    parser.add_argument('--output_path', type=str, required=True, help='輸出處理後的 JSON 檔案路徑')
    
    args = parser.parse_args()

    process_faq_data(args.source_path, args.output_path)