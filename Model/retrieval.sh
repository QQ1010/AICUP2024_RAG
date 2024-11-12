python retrieval.py \
    --question_path ../Data/dataset/preliminary/questions_example.json \
    --source_dir ../Preprocess/Data \
    --output_dir ../Data/dataset/results \
    --strategy reranker \
    --model_name BAAI/bge-reranker-v2-m3 \
    --is_use_summary False \