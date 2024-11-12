import os
import json
import argparse
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed

import pdfplumber
import pytesseract
from tqdm import tqdm
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance


def preprocess_image(image):
    """
    增強圖片對比度並進行二值化，以提升 OCR 的準確度。
    """
    image = image.convert('L')  # 轉成灰階
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # 提升對比度
    image = image.point(lambda x: 0 if x < 150 else 255, '1')  # 調整閾值以去除雜訊
    return image

def ocr_image(image):
    """
    使用 Tesseract 進行圖片文字辨識。
    """
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=0'
    text = pytesseract.image_to_string(image, lang='chi_tra', config=custom_config)
    return text

def ocr_pdf(pdf_loc):
    """
    使用圖片轉換和 OCR 對 PDF 進行文字辨識。
    """
    try:
        images = convert_from_path(pdf_loc)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return ""

    all_text = ""
    for image in images:
        try:
            processed_image = preprocess_image(image)
            text = ocr_image(processed_image)
            all_text += text + "\n"
        except Exception as e:
            print(f"Error processing image for OCR: {e}")
    
    return all_text

def extract_text_from_pdf(pdf_loc, page_infos=None):
    """
    優先嘗試直接從 PDF 提取文字，失敗則使用 OCR。
    """
    pdf_text = ""
    try:
        with pdfplumber.open(pdf_loc) as pdf:
            pages = pdf.pages[page_infos[0]:page_infos[1]] if page_infos else pdf.pages
            for page in pages:
                text = page.extract_text()
                if text:
                    pdf_text += text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")

    # 如果無法從 PDF 提取文字，則使用 OCR
    if not pdf_text.strip():
        pdf_text = ocr_pdf(pdf_loc)
    
    return pdf_text

def write_text_to_file(text, output_folder, file_name):
    """
    將文字寫入檔案。
    """
    file_name = file_name.replace('.pdf', '_text.txt')
    file_path = os.path.join(output_folder, file_name)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f"Error writing file {file_name}: {e}")

def main(source_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [file for file in os.listdir(source_folder) if file.endswith('.pdf')]
    pdf_locs = [os.path.join(source_folder, file) for file in pdf_files]

    cpu_count = os.cpu_count()
    with ProcessPoolExecutor(max_workers=cpu_count // 2) as executor:
        futures = {executor.submit(extract_text_from_pdf, pdf_loc): pdf_loc for pdf_loc in pdf_locs}
        for future in tqdm(as_completed(futures), total=len(pdf_files)):
            pdf_loc = futures[future]
            try:
                text = future.result()
                write_text_to_file(text, output_folder, os.path.basename(pdf_loc))
            except Exception as e:
                print(f"Error processing {pdf_loc}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process some paths and files.')
    parser.add_argument('--source_folder', type=str,
                        required=True, help='讀取 PDF 檔案的資料夾路徑')
    parser.add_argument('--output_folder', type=str,
                        required=True, help='輸出文字檔案的資料夾路徑')

    args = parser.parse_args()

    main(args.source_folder, args.output_folder)