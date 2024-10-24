import os
import json
import argparse
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm
import pdfplumber


def load_data(source_path):
    masked_file_ls = [file for file in os.listdir(source_path) if file.endswith('.pdf')]
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(read_pdf, [os.path.join(source_path, file) for file in masked_file_ls]), total=len(masked_file_ls)))
    corpus_dict = {int(file.replace('.pdf', '')): result for file, result in zip(masked_file_ls, results)}
    return corpus_dict


def read_pdf(pdf_loc, page_infos: list = None):
    try:
        pdf = pdfplumber.open(pdf_loc)

        pages = pdf.pages[page_infos[0]:page_infos[1]
                          ] if page_infos else pdf.pages
        pdf_text = ''
        for _, page in enumerate(pages):
            text = page.extract_text()
            if text:
                pdf_text += text
        pdf.close()
        return pdf_text
    except Exception as e:
        print(f"Error reading {pdf_loc}: {e}")
        return ""


def load_faq_data(source_path):
    corpus_dict_faq = {}
    with open(source_path, 'r') as f:
        key_to_source_dict = json.load(f)
        for key, value in key_to_source_dict.items():
            content = ''
            for item in value:
                content += (item['question'] + '、'.join(item['answers']))
            corpus_dict_faq[key] = content
    return corpus_dict_faq


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process some paths and files.')
    parser.add_argument('--source_path', type=str,
                        default='Data/reference', help='讀取參考資料路徑')
    parser.add_argument('--output_path', type=str,
                        default='Data/reference/processed', help='輸出預處理過後的檔案路徑')

    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)

    # 處理pdf資料
    pdf_category = ['insurance', 'finance']
    for category in pdf_category:
        source_path = os.path.join(args.source_path, category)
        corpus_dict = load_data(source_path)
        sorted_corpus_dict = dict(sorted(corpus_dict.items()))
        with open(os.path.join(args.output_path, f'{category}.json'), 'w', encoding='utf8') as f:
            json.dump(sorted_corpus_dict, f, ensure_ascii=False, indent=4)

    # 處理faq資料
    source_path_faq = os.path.join(
        args.source_path, 'faq/pid_map_content.json')
    corpus_dict_faq = load_faq_data(source_path_faq)
    sorted_corpus_dict_faq = dict(sorted(corpus_dict_faq.items()))
    with open(os.path.join(args.output_path, 'faq.json'), 'w', encoding='utf8') as f:
        json.dump(sorted_corpus_dict_faq, f, ensure_ascii=False, indent=4)
