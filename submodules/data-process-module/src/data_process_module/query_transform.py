import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class QueryTransform:
    def __init__(self) -> None:
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
        )
        self.model = "qwen/qwen-2.5-72b-instruct:free"

    def decompose_query(self, query: str, n: int = 3) -> list[str]:
        completion = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Decompose the query into {n} simple questions: {query}. No explanation needed, just the sub-queries in a list. No numbering or bullet points, just plain text. Maintain the original language of the query.",
                }
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("No content returned from OpenAI API")
        return content.splitlines()

    def extract_keywords(self, query: str) -> list[str]:
        completion = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract keywords from the query: {query}. No explanation needed, just the keywords in a comma-separated list. Maintain the original language of the query.",
                }
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("No content returned from OpenAI API")
        return content.split(", ")


if __name__ == "__main__":
    query_transform = QueryTransform()
    query = "Người lao động không nghỉ việc khi nhận con nuôi thì mức trợ cấp BHXH một lần được hưởng là bao nhiêu tiền?"
    subquries = query_transform.decompose_query(query)
    print(subquries)
    keywords = query_transform.extract_keywords(query)
    print(keywords)