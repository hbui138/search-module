def flatten(corpus):
    flattened = []
    for doc in corpus:
        for article in doc["content"]:
            flattened.append(
                {
                    "aid": article["aid"],
                    "content_Article": article["content_Article"],
                    "law_id": doc["law_id"],
                    "doc_id": doc["id"],
                }
            )
    return flattened