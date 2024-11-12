import os
import json
import argparse

from tqdm import tqdm
import pdfplumber  # 用於從PDF文件中提取文字的工具
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# 載入參考資料，返回一個字典，key為檔案名稱，value為PDF檔內容的文本
def load_data(source_path):
    masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
    corpus_dict = {int(file.replace('.pdf', '')): read_pdf(os.path.join(source_path, file)) for file in tqdm(masked_file_ls)}  # 讀取每個PDF文件的文本，並以檔案名作為鍵，文本內容作為值存入字典
    return corpus_dict

# 讀取單個PDF文件並返回其文本內容
def read_pdf(pdf_loc, page_infos: list = None):
    pdf = pdfplumber.open(pdf_loc)  # 打開指定的PDF文件

    # 如果指定了頁面範圍，則只提取該範圍的頁面，否則提取所有頁面
    pages = pdf.pages[page_infos[0]:page_infos[1]] if page_infos else pdf.pages
    pdf_text = ''
    pdf_tables = []
    pdf_images = []
    for _, page in enumerate(pages):  # 迴圈遍歷每一頁
        
        text = page.extract_text()  # 提取頁面的文本內容
        if text:
            pdf_text += text
        
        tables = page.extract_tables()  # 提取頁面中的表格
        if tables:
            pdf_tables.extend(tables)  # 存儲所有表格數據

        images = page.images            # 提取頁面中的圖片
        if images:
            pdf_images.extend(images)  # 存儲所有圖片位置資訊

    pdf.close()  # 關閉PDF文件

    ## 將 pdf_text, pdf_tables, pdf_images 存入 .txt 檔案，須包含檔案名字
    # 提取文件名和來源資料夾（如 finance 或 insurance）
    base_filename = os.path.splitext(os.path.basename(pdf_loc))[0]
    sub_dir = os.path.basename(os.path.dirname(pdf_loc))  # 這裡抓取 'finance' 或 'insurance'
    
    # 構建輸出路徑
    output_dir = os.path.join('Data', sub_dir)

    # 確保輸出資料夾存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # 生成相應的文件名並儲存在適當的資料夾下
    text_filename = os.path.join(output_dir, f"{base_filename}_text.txt")
    table_filename = os.path.join(output_dir, f"{base_filename}_table.txt")
    image_filename = os.path.join(output_dir, f"{base_filename}_image.txt")

    with open(text_filename, 'w', encoding='utf8') as f:
        f.write(pdf_text)
    if pdf_tables:
        with open(table_filename, 'w', encoding='utf8') as f:
            f.write(str(pdf_tables))
    if pdf_images:
        with open(image_filename, 'w', encoding='utf8') as f:
            f.write(str(pdf_images))
    
    # 產生 Summary 檔案
    summarize_text(text_filename)

    return pdf_text  # 返回萃取出的文本

# 總結文字內容，將其轉換為一個字串
def summarize_text(txt_loc):
    with open(txt_loc, 'r', encoding='utf8') as f:
        article_text = f.read()
    
    # 讀入 summary 模型
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
    model_name = "csebuetnlp/mT5_multilingual_XLSum"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # 使用 GPU 如果可用
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)  # 將模型移動到 GPU

    summaries = []
    paragraphs = _split_by_length_with_overlap(article_text, length=256, overlap=100)
    for paragraph in paragraphs:
        input_ids = tokenizer(
                        [WHITESPACE_HANDLER(paragraph)],
                        return_tensors="pt",
                        padding="max_length",
                        truncation=True,
                        max_length=512
                    )["input_ids"].to(device)  # 將 input_ids 也移動到 GPU

        output_ids = model.generate(
                        input_ids=input_ids,
                        max_length=512,
                        no_repeat_ngram_size=2,
                        num_beams=4
                    )[0]

        summary = tokenizer.decode(
                        output_ids,
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=False
                    )
        summaries.append(summary)
    
    # 檔案名字，摘取 txt_loc 並加上後綴 _summary.txt，txt_loc 是 Data/finance/*.txt 或 Data/insurance/*.txt ，存到txt_loc同一個資料夾
    base_filename = os.path.splitext(os.path.basename(txt_loc))[0]
    sub_dir = os.path.basename(os.path.dirname(txt_loc))  # 這裡抓取 'finance' 或 'insurance'
    output_dir = os.path.join('Data', sub_dir)
    summary_filename = os.path.join(output_dir, f"{base_filename}_summary.txt")

    # 將 summary 寫入文件
    with open(summary_filename, 'w', encoding='utf8') as f:
        for summary in summaries:
            f.write(summary + '\n')

    return summaries

# 將文本按照指定的長度和重疊進行分割
def _split_by_length_with_overlap(text, length=100, overlap=20):
        paragraphs = []
        i = 0
        while i < len(text):
            paragraphs.append(text[i:i+length])
            i += length - overlap
        return paragraphs


if __name__ == "__main__":
    # 使用argparse解析命令列參數
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料路徑')  # 參考資料的路徑

    args = parser.parse_args()  # 解析參數

    source_path_insurance = os.path.join(args.source_path, 'insurance')  # 設定參考資料路徑
    corpus_dict_insurance = load_data(source_path_insurance)

    source_path_finance = os.path.join(args.source_path, 'finance')  # 設定參考資料路徑
    corpus_dict_finance = load_data(source_path_finance)