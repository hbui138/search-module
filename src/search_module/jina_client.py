import json
import os
import urllib.parse
from typing import TypedDict

import requests
from dotenv import load_dotenv
from more_itertools import chunked

load_dotenv()


class RankItem(TypedDict):
    index: str
    relevance_score: float


class Jina:
    def __init__(self) -> None:
        self.endpoint = os.getenv("JINA_ENDPOINT", "https://api.jina.ai/v1/")
        self.api_key = os.getenv("JINA_API_KEY", None)

    def embed(self, text_list: list[str], task: str = "") -> list[list[float]]:
        """https://huggingface.co/jinaai/jina-embeddings-v3"""
        url = urllib.parse.urljoin(self.endpoint, "embeddings")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": "jina-embeddings-v3",
            "truncate": True,
            "input": text_list,
        }
        if task:
            data["task"] = task
        response = requests.post(url, headers=headers, data=json.dumps(data))

        embedding_list = []
        for i in response.json().get("data", []):
            embedding_list.append(i.get("embedding", []))
        return embedding_list

    def embed_by_batch(
        self, text_list: list[str], task: str = "", batch_size: int = 8
    ) -> list[list[float]]:
        """Embed text in batches to avoid large payloads."""
        embedding_list = []
        for batch in chunked(text_list, batch_size):
            embedding_list.extend(self.embed(batch, task))
        return embedding_list

    def rerank(
        self, query: str, text_list: list[str], top_n: int = 3
    ) -> list[RankItem]:
        """https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual"""
        url = urllib.parse.urljoin(self.endpoint, "rerank")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "documents": text_list,
            "top_n": top_n,
            "return_documents": False,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        rank_list = []
        for i in response.json().get("results", []):
            rank_list.append(i)
        return rank_list


if __name__ == "__main__":
    jina_client = Jina()
    query = "What is the capital of France?"
    text_list = ["Hanoi is the capital of Vietnam.", "Paris is the capital of France.", "The dog is big.", "The cat is small."]
    print(jina_client.rerank(query, text_list))
