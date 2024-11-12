# 資料前處理

## 安裝
#### 注意：要在 Python 3 的環境
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

## 執行
```
python data_preprocess.py --source_path ../Data/reference
```
source_path Data/reference 中要是儲存 finance 和 insurance 的所有 pdf 檔案

## 結果
前處理後的資料會存到
Preprocess/Data/insurance
Preprocess/Data/finance