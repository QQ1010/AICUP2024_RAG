# 資料前處理 (Data Preprocessing)
## 執行
#### 使用 ORC 將 pdf 轉圖片後轉文字
```
python data_preprocess.py --source_folder ../Data/reference/finance --output_folder Data/finance

python data_preprocess.py --source_folder ../Data/reference/insurance --output_folder Data/insurance
```
#### 產生 FAQ 檔案
```
python faq_text_concate.py --source_path ../Data/reference/faq/pid_map_content.json --output_path Data/faq.json
```

#### 產生文字檔與summary (Optional，可不執行)
source_path Data/reference 中要是官方公告的 finance 和 insurance 的所有 pdf 檔案
json_source_path 是官方公告的 faq 檔案
```
python generate_summary.py \
    --source_path ../Data/reference
```

## 結果
前處理後的資料會存到
Preprocess/Data/insurance
Preprocess/Data/finance
Preprocess/Data/faq.json

## 資料夾說明
```
├ Preprocess
| ├ Data                     ## 前處理後的資料，執行 data_preprocess.py 後產生
| | ├ finance
| | | 1_text.txt
| | | 1_text_summary.txt (optional)
| | └ ...
| | ├ insurance
| | | 1_text.txt
| | | 1_text_summary.txt (optional)
| | └ ...
| | └ faq.json
│ ├ data_preprocess.py
│ ├ faq_text_concate.py
│ ├ pdf2txt.py
│ └ README.md
```