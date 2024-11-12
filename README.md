# AI CUP 2024 玉山人工智慧公開挑戰賽 － RAG與LLM在金融問答的應用

## 競賽說明
「當 LLM 開創了人人使用 AI 的時代，你準備好了嗎？」
在大型語言模型加速催化各式技術的年代，語言模型的開發週期越來越短、效能越來越強。隨著大型語言模型的問世，金融業龐大且複雜的資料已經不再是語料檢索無法高度泛化的障礙，而是逐漸被解決的問題。
本屆挑戰賽聚焦在金融問答領域，提供豐富的資料庫供參賽者使用。參賽者需設計機制以提高檢索結果的準確性，包括從提供的語料中找出完整回答問題的正確資料等基本要求，以及應用大型語言模型的生成能力，產出正確且完整的回答。
準備好了的話，現在就報名參加挑戰吧！

## 相關連結
- [T-Brain 官網](https://tbrain.trendmicro.com.tw/Competitions/Details/37)
- [AI CUP 官網](https://www.aicup.tw/ai-cup-2024-competition)

## 資料夾說明
```
.
├ Preprocess
| ├ Data                     ## 前處理後的資料，執行 data_preprocess.py 後產生
| | ├ finance
| | | 1_text.txt
| | | 1_text_summary.txt
| | └ ...
| | ├ insurance
| | | 1_text.txt
| | | 1_text_summary.txt
| | └ ...
| | └ faq.json
│ ├ data_preprocess.py
│ ├ faq_text_concate.py
│ ├ pdf2txt.py
│ └ README.md
├ Model
│ ├ retrieval.py
│ ├ retrieval.sh
│ ├ data_interface.py
│ └ README.md
├ Data                       // 原始資料(需自行下載)
| ├ dataset
| │ ├ preliminary
| | └ questions_example.json  // Retrieve 問題
| │ ├ results
| | └ pred_retrieve.json      // Retrieve 結果
| ├ reference
| │ ├ finance
| | | 1.pdf
| | | ..
| | └ 1034.pdf 
| │ ├ insurance
| | | 1.pdf
| | | ..
| | └ 643.pdf 
| │ ├ faq
| | └ pid_map_content.json
├ requirements.txt
├ .gitignore
└ README.md
```
注意 Data 資料集的內容需要先從官方檔案中下載

## 安裝
#### 注意：要在 Python 3 的環境
Python=3.9.20
```
conda create -n aicup python=3.9.20
```
#### 安裝套件
```
pip install -r requirements.txt
```

#### 安裝 Pytorch
```
> conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
> conda install conda-forge::transformers
> pip install sentencepiece
> pip install tokenizers
> pip install protobuf
```
#### Conda packages
```
conda install -c conda-forge tesseract=5.3.1
conda install -c anaconda poppler=22.12.0
```

## 執行與使用
1. 前往 Preprocess 資料夾中的 README.md 按照執行步驟產生資料
2. 前往 Model 資料夾中的 README.md 按照執行步驟產生結果

注意事項
使用 bash 檔時，請檢查路徑是否正確