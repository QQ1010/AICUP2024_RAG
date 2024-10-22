import os
import json
import argparse

from tqdm import tqdm
import jieba  # 用於中文文本分詞
import pdfplumber  # 用於從PDF文件中提取文字的工具
from rank_bm25 import BM25Okapi  # 使用BM25演算法進行文件檢索

# 載入參考資料，返回一個字典，key為檔案名稱，value為PDF檔內容的文本
def load_data(source_path):
    masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
    corpus_dict = {int(file.replace('.pdf', '')): read_pdf(os.path.join(source_path, file)) for file in tqdm(masked_file_ls)}  # 讀取每個PDF文件的文本，並以檔案名作為鍵，文本內容作為值存入字典
    return corpus_dict

# 讀取單個PDF文件並返回其文本內容
def read_pdf(pdf_loc, page_infos: list = None):
    pdf = pdfplumber.open(pdf_loc)  # 打開指定的PDF文件

    # TODO: 可自行用其他方法讀入資料，或是對pdf中多模態資料（表格,圖片等）進行處理

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
        # 套件安裝失敗且出現衝突使程式無法執行 (尚未解決)
        # if images:
        #     for img in images:
        #         # 取得圖片的座標信息，從PDF中提取該圖片
        #         img_bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
        #         image_data = page.within_bbox(img_bbox).to_image()
        #         # 將圖片轉換為PIL格式，以便使用Tesseract進行OCR
        #         pil_img = Image.open(BytesIO(image_data.original))
        #         # 使用Tesseract來提取圖片中的文字
        #         ocr_text = pytesseract.image_to_string(pil_img, lang = 'chi_tra')
        #         pdf_images.append(ocr_text)  # 將OCR提取的文字加入清單

    pdf.close()  # 關閉PDF文件

    ## 將 pdf_text, pdf_tables, pdf_images 存入 .txt 檔案，須包含檔案名字
    # 提取文件名和來源資料夾（如 finance 或 insurance）
    base_filename = os.path.splitext(os.path.basename(pdf_loc))[0]
    sub_dir = os.path.basename(os.path.dirname(pdf_loc))  # 這裡抓取 'finance' 或 'insurance'
    
    # 構建輸出路徑
    output_dir = os.path.join('Data', 'dataPreprocessing', sub_dir)

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


    return pdf_text  # 返回萃取出的文本


# 根據查詢語句和指定的來源，檢索答案
def BM25_retrieve(qs, source, corpus_dict):
    filtered_corpus = [corpus_dict[int(file)] for file in source]

    # [TODO] 可自行替換其他檢索方式，以提升效能

    tokenized_corpus = [list(jieba.cut_for_search(doc)) for doc in filtered_corpus]  # 將每篇文檔進行分詞
    bm25 = BM25Okapi(tokenized_corpus)  # 使用BM25演算法建立檢索模型
    tokenized_query = list(jieba.cut_for_search(qs))  # 將查詢語句進行分詞
    ans = bm25.get_top_n(tokenized_query, list(filtered_corpus), n=1)  # 根據查詢語句檢索，返回最相關的文檔，其中n為可調整項
    a = ans[0]
    # 找回與最佳匹配文本相對應的檔案名
    res = [key for key, value in corpus_dict.items() if value == a]
    return res[0]  # 回傳檔案名


if __name__ == "__main__":
    # 使用argparse解析命令列參數
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--question_path', type=str, required=True, help='讀取發布題目路徑')  # 問題文件的路徑
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料路徑')  # 參考資料的路徑
    parser.add_argument('--output_path', type=str, required=True, help='輸出符合參賽格式的答案路徑')  # 答案輸出的路徑
    parser.add_argument('--save_pageInfo', type=bool, default=False, help='是否要儲存 PDF 資訊') # 是否要儲存 PDF 資訊
    parser.add_argument('--pageInfo', type=list, default=None, help='PDF 頁面範圍') # 指定要讀取的頁面範圍

    args = parser.parse_args()  # 解析參數

    answer_dict = {"answers": []}  # 初始化字典

    with open(args.question_path, 'rb') as f:
        qs_ref = json.load(f)  # 讀取問題檔案

    source_path_insurance = os.path.join(args.source_path, 'insurance')  # 設定參考資料路徑
    corpus_dict_insurance = load_data(source_path_insurance)

    source_path_finance = os.path.join(args.source_path, 'finance')  # 設定參考資料路徑
    corpus_dict_finance = load_data(source_path_finance)

    with open(os.path.join(args.source_path, 'faq/pid_map_content.json'), 'rb') as f_s:
        key_to_source_dict = json.load(f_s)  # 讀取參考資料文件
        key_to_source_dict = {int(key): value for key, value in key_to_source_dict.items()}

    for q_dict in qs_ref['questions']:
        if q_dict['category'] == 'finance':
            # 進行檢索
            retrieved = BM25_retrieve(q_dict['query'], q_dict['source'], corpus_dict_finance)
            # 將結果加入字典
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        elif q_dict['category'] == 'insurance':
            retrieved = BM25_retrieve(q_dict['query'], q_dict['source'], corpus_dict_insurance)
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        elif q_dict['category'] == 'faq':
            corpus_dict_faq = {key: str(value) for key, value in key_to_source_dict.items() if key in q_dict['source']}
            retrieved = BM25_retrieve(q_dict['query'], q_dict['source'], corpus_dict_faq)
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        else:
            raise ValueError("Something went wrong")  # 如果過程有問題，拋出錯誤

    # 將答案字典保存為json文件
    with open(args.output_path, 'w', encoding='utf8') as f:
        json.dump(answer_dict, f, ensure_ascii=False, indent=4)  # 儲存檔案，確保格式和非ASCII字符
