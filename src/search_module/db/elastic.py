import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

load_dotenv()

DEFAULT_SETTINGS = {
    "similarity": {"my_bm25": {"type": "BM25", "b": 0.75}},
    "analysis": {
        "analyzer": {
            "my_vi_analyzer": {
                "tokenizer": "vi_tokenizer",
                "filter": ["lowercase", "ascii_folding"],
            },
            "code_analyzer": {
                "tokenizer": "code_tokenizer",
                "filter": ["lowercase", "ascii_folding"],
            },
        },
        "tokenizer": {
            "code_tokenizer": {
                "type": "pattern",
                "pattern": "[ !\"#$%&'()*+,.:;<=>?@\\^_`{|}~]",
                "lowercase": "true",
            }
        },
        "filter": {
            "ascii_folding": {"type": "asciifolding", "preserve_original": "true"}
        },
    },
}

DEFAULT_MAPPINGS = {
    "properties": {
        "aid": {"type": "integer", "index": False},
        "content_Article": {
            "type": "text",
            "analyzer": "my_vi_analyzer",
            "similarity": "my_bm25",
        },
        "law_id": {"type": "text", "analyzer": "code_analyzer"},
        "doc_id": {"type": "integer", "index": False},
    }
}


class Elastic:
    def __init__(self) -> None:
        self.client = Elasticsearch(
            os.getenv("ES_HOST", "http://localhost:9200"),
            basic_auth=(
                os.getenv("ES_USER", "elastic"),
                os.getenv("ES_PASSWORD", "empty"),
            ),
        )

    def check_health(self) -> bool:
        return self.client.ping()

    def init_index(self, index_name: str):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(
                index=index_name, mappings=DEFAULT_MAPPINGS, settings=DEFAULT_SETTINGS
            )
            return True
        return False

    def bulk_upload(self, index_name: str, datapoints: list[dict]):
        bulk_data = []
        for i in datapoints:
            if "embedding" in i:
                bulk_data.append({k: v for k, v in i.items() if k != "embedding"})
            else:
                bulk_data.append(i)
        return helpers.bulk(self.client, bulk_data, index=index_name, refresh=True)


if __name__ == "__main__":
    print("Connecting to ElasticSearch...")
    elastic = Elastic()
    if elastic.check_health():
        print("Connection successful!")
    else:
        print("Connection failed!")
