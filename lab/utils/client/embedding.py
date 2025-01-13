import logging
import requests
from typing import List
from langchain_core.embeddings import Embeddings


class EmbeddingClient(Embeddings):

    def __init__(self, embedding_api_path: str, request_timeout: int = 600):
        self.embedding_api_path = embedding_api_path
        self.request_timeout = request_timeout

    def embed_documents(
        self, documents: List[str]
    ) -> List[List[float]]:

        try:
            response = requests.post(
                self.embedding_api_path,
                json={'documents': documents},
                timeout=self.request_timeout
            )
            return response.json()['embeddings']
        
        except requests.exceptions.Timeout as timeout_exception:
            logging.error(str(timeout_exception))
            raise timeout_exception
        
        except requests.exceptions.RequestException as exc:
            logging.error(str(exc))
            raise exc
        
    def embed_query(self, query: str) -> List[float]:
        return self.embed_documents([query])[0]