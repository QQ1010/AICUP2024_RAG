from pdf2image import convert_from_path
import pytesseract

def ocr_pdf(pdf_loc):
    images = convert_from_path(pdf_loc)
    all_text = ""
    for image in images:
        text = pytesseract.image_to_string(
            image, lang='chi_tra') + "\n"  # 設定語言為繁體中文
        all_text += text

    return all_text


pdf_path = '/home/guest/r12922a14/AICUP2024_RAG/Data/reference/finance/1.pdf'  # 替換成您 PDF 檔案的路徑
images = convert_from_path(pdf_path)

# 使用 pytesseract 偵測每頁圖像的文字
all_text = ""
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image, lang='chi_tra') + "\n"  # 設定語言為繁體中文
    all_text += text

# 輸出結果
print(all_text)
