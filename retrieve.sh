export CUDA_VISIBLE_DEVICES=2

python retrieve.py \
    --question_path Data/dataset/preliminary/questions_example.json \
    --source_dir Data/reference/processed \
    --output_dir Data/dataset/results \
    --strategy reranker \
    --model_name BAAI/bge-reranker-v2-m3 \