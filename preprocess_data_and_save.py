import os
import json
import argparse
from concurrent.futures import ProcessPoolExecutor

import pdfplumber
import pytesseract
from tqdm import tqdm
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance


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


def load_data(source_path):
    masked_file_ls = [file for file in os.listdir(
        source_path) if file.endswith('.pdf')]
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(read_pdf, [os.path.join(
            source_path, file) for file in masked_file_ls]), total=len(masked_file_ls)))
    corpus_dict = {int(file.replace('.pdf', '')): result for file,
                   result in zip(masked_file_ls, results)}
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

        if pdf_text == '':
            print(pdf_loc)
            pdf_text += ocr_pdf(pdf_loc)
        return pdf_text
    except Exception as e:
        print(f"Error reading {pdf_loc}: {e}")
        return ""


def ocr_pdf(pdf_loc):
    images = convert_from_path(pdf_loc)
    all_text = ""
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=0'

    for image in images:
        image = preprocess_image(image)
        text = pytesseract.image_to_string(
            image, lang='chi_tra', config=custom_config) # 設定語言為繁體中文
        # text = ' '.join(text.split())
        all_text += text + "\n" 

    return all_text


def preprocess_image(image):
    # 轉為灰度
    image = image.convert('L')
    # 提高對比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # 二值化
    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    return image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process some paths and files.')
    parser.add_argument('--source_path', type=str,
                        default='Data/reference', help='讀取參考資料路徑')
    parser.add_argument('--output_path', type=str,
                        default='Data/reference/processed', help='輸出預處理過後的檔案路徑')

    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)

    # # 處理pdf資料
    # pdf_category = ['insurance', 'finance']
    # for category in pdf_category:
    #     source_path = os.path.join(args.source_path, category)
    #     corpus_dict = load_data(source_path)
    #     sorted_corpus_dict = dict(sorted(corpus_dict.items()))
    #     with open(os.path.join(args.output_path, f'{category}.json'), 'w', encoding='utf8') as f:
    #         json.dump(sorted_corpus_dict, f, ensure_ascii=False, indent=4)

    # # 處理faq資料
    # source_path_faq = os.path.join(
    #     args.source_path, 'faq/pid_map_content.json')
    # corpus_dict_faq = load_faq_data(source_path_faq)
    # sorted_corpus_dict_faq = dict(sorted(corpus_dict_faq.items()))
    # with open(os.path.join(args.output_path, 'faq.json'), 'w', encoding='utf8') as f:
    #     json.dump(sorted_corpus_dict_faq, f, ensure_ascii=False, indent=4)

    ori_path = os.path.join("Data", "reference", 'finance')
    base_path = os.path.join("Data", "dataPreprocessing", 'finance')
    file_names = [f for f in os.listdir(base_path) if f.endswith("_text.txt")]
    file_names = sorted(file_names)
    for file_name in tqdm(file_names):
        print(f"處理檔案 {file_name}")
        file_path = os.path.join(base_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"檔案 {file_path} 不存在，跳過此檔案。")
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
        
        if text == '':
            id = file_name.split('_')[0]
            pdf_path = os.path.join(ori_path, f"{id}.pdf")
            ocr_text = ocr_pdf(pdf_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ocr_text)
        

    # test_path = '/home/guest/r12922a14/AICUP2024_RAG/Data/reference/finance/1.pdf'
    # ocr_text = ocr_pdf(test_path)
    # with open('1_w_config_and_img_enhance.txt', 'w', encoding='utf-8') as f:
        # f.write(ocr_text)
