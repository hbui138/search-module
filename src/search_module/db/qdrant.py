import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

load_dotenv()


class Qdrant:
    def __init__(self) -> None:
        self.client = QdrantClient(
            url=os.getenv("QDRANT_HOST", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY", None),
        )

    def check_health(self) -> bool:
        try:
            self.client.info()
            return True
        except Exception as e:
            return False

    def init_collection(self, collection_name: str, embedding_size: int = 1024):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embedding_size, distance=Distance.COSINE
                ),
            )
            return True
        return False
    
    def bulk_upload(self, collection_name: str, datapoints: list[dict]):
        points = []
        for data in datapoints:
            embedding = data.get("embedding", [])
            payload = {k: v for k, v in data.items() if k != "embedding"}
            # Use a unique ID (aid) for each point
            point_id = payload.get("aid")
            if point_id is None:
                continue  # skip if no unique id
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
        return self.client.upsert(collection_name=collection_name, points=points)


if __name__ == "__main__":
    print("Connecting to Qdrant...")
    qdrant = Qdrant()
    if qdrant.check_health():
        print("Connection successful!")
    else:
        print("Connection failed!")
