import argparse
import json
import os
from abc import ABC, abstractmethod

import jieba  # 用於中文文本分詞
from tqdm import tqdm
from rank_bm25 import BM25Okapi  # 使用BM25演算法進行文件檢索
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagModel
from FlagEmbedding import FlagReranker

from data_interface import MyDataset


class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query, source_id, source_context):
        pass


class BM25Retriever(RetrievalStrategy):
    def __init__(self):
        pass

    def retrieve(self, query, source_id, source_context):
        tokenized_corpus = [list(jieba.cut_for_search(doc))
                            for doc in source_context]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = list(jieba.cut_for_search(query))
        docs = bm25.get_top_n(tokenized_query, list(source_context), n=1)
        ans_id = source_id[source_context.index(docs[0])]
        return ans_id


class BiEncorderRetriever(RetrievalStrategy):
    def __init__(self, model_name, framework='sentence-transformers'):
        if framework == 'sentence-transformers':
            self.model = SentenceTransformer(model_name)
        elif framework == 'flag':
            self.model = FlagModel(model_name,
                                   query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                                   use_fp16=True)

    def retrieve(self, query, source_id, source_context):
        embedding = self.model.encode(
            source_context, normalize_embeddings=True)
        query_embedding = self.model.encode(
            query, normalize_embeddings=True)
        similarity = (embedding @ query_embedding.T).squeeze()
        ans_id = source_id[similarity.argmax()]
        return ans_id

    def score(self, query, source_context):
        embedding = self.model.encode(
            source_context, normalize_embeddings=True)
        query_embedding = self.model.encode(
            query, normalize_embeddings=True)
        similarity = (embedding @ query_embedding.T)
        return max(similarity)


class RerankRetriever(RetrievalStrategy):
    def __init__(self, model_name):
        self.reranker = FlagReranker(model_name, use_fp16=True)

    def retrieve(self, query, source_id, source_context):
        query_doc_pairs = [[query, doc] for doc in source_context]
        score = self.reranker.compute_score(query_doc_pairs, normalize=True)
        ans_id = source_id[score.index(max(score))]
        return ans_id

    def score(self, query, source_context):
        query_doc_pairs = [[query, doc] for doc in source_context]
        score = self.reranker.compute_score(query_doc_pairs, normalize=True)
        return max(score)


class Retriever:
    def __init__(self, strategy: RetrievalStrategy):
        self.strategy = strategy

    def retrieve(self, sample):
        return self.strategy.retrieve(sample["query"], sample["source"], sample["source_context"])

    def retrieve_by_paragraph(self, sample):
        source_context_score = []
        for context in sample["source_context"]:
            if context == '':
                source_context_score.append(0)
                continue
            paragraphs = self._split_by_length_with_overlap(context, 450, 100)
            score = self.strategy.score(
                sample["query"], paragraphs)
            source_context_score.append(score)
        # if sample["qid"] == 51:
        #     print(source_context_score)
        #     breakpoint()
        return sample["source"][source_context_score.index(max(source_context_score))]

    def _split_by_length_with_overlap(self, text, length=100, overlap=20):
        paragraphs = []
        i = 0
        while i < len(text):
            paragraphs.append(text[i:i+length])
            i += length - overlap
        return paragraphs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process some paths and files.')
    parser.add_argument('--question_path', type=str,
                        required=True, help='讀取發布題目路徑')
    parser.add_argument('--source_dir', type=str,
                        required=True, help='讀取參考資料路徑')
    parser.add_argument('--output_dir', type=str,
                        required=True, help='輸出符合參賽格式的答案路徑')
    parser.add_argument('--strategy', type=str, default='bm25', choices=['bm25', 'biencoder', 'reranker', 'flag'],
                        help='選擇檢索策略，預設為bm25')
    parser.add_argument('--model_name', type=str, default=None,
                        help='選擇模型名稱，當使用 bm25 以外的策略時需要指定')

    args = parser.parse_args()

    if args.strategy != 'bm25' and not args.model_name:
        parser.error("當選擇非 'bm25' 策略時，必須指定 --model_name")

    dataset = MyDataset(args.question_path, args.source_dir)

    if args.strategy == 'bm25':
        retriever = Retriever(BM25Retriever())
        output_file_name = 'bm25.json'
    elif args.strategy == 'biencoder':
        retriever = Retriever(BiEncorderRetriever(args.model_name))
    elif args.strategy == 'reranker':
        retriever = Retriever(RerankRetriever(args.model_name))
    elif args.strategy == 'flag':
        retriever = Retriever(BiEncorderRetriever(args.model_name, framework='flag'))

    if args.model_name:
        model_name = args.model_name.replace('/', '_').replace('-', '_')
        output_file_name = f'{args.strategy}_{model_name}.json'

    answer_dict = {"answers": []}  # 初始化字典
    for i in tqdm(range(len(dataset))):
        sample = dataset[i]
        ans = retriever.retrieve_by_paragraph(sample)
        answer_dict["answers"].append({"qid": sample["qid"], "retrieve": ans})

    output_path = os.path.join(args.output_dir, output_file_name)
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(answer_dict, f, ensure_ascii=False,
                  indent=4)  # 儲存檔案，確保格式和非ASCII字符
