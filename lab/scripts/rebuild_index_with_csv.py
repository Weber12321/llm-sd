from ast import literal_eval
from typing import Dict, List, cast
import pandas as pd

from urllib.parse import urlparse
from utils.opensearch_client import OpenSearchClient
from utils.send_requests import send_post_request


API_BASE_URL = ""
LLM_BASE_URL = ""
OPENSEARCH_URL = ""
parsed_url = urlparse(OPENSEARCH_URL)

opensearch = OpenSearchClient(
    str(parsed_url.hostname), int(cast(str, parsed_url.port))
)


def chunks_to_embedding(df: pd.DataFrame) -> List[Dict]:
    df['Metadata'] = df['Metadata'].apply(literal_eval)
    chunks = df.to_dict("records")
    url = f"{LLM_BASE_URL}/api/v0/embedding/doc"
    data = {"documents": [chunk["Text"] for chunk in chunks]}
    response = cast(Dict, send_post_request(url, data))
    for chunk, embedding in zip(chunks, response["embeddings"]):
        chunk["embedding"] = embedding
    return chunks


def save_chunk_to_db(chunks: List[Dict], index: str):
    documents = []
    for chunk in chunks:
        document = {
            "vector_field": chunk["embedding"],
            "text": chunk["Text"],
            "metadata": chunk["Metadata"],
        }
        documents.append(document)

    opensearch.add_documents(index, documents=documents)


def data_process(
    df: pd.DataFrame,
    index: str
):
    list_of_chunks = chunks_to_embedding(df)
    save_chunk_to_db(list_of_chunks, index)


def create_index(
    index: str,
    db_name: str,
    embedding_model: str,
    chunk_size: int,
    overlap: int,
):
    url = f"{LLM_BASE_URL}/api/v0/embedding/doc"
    data = {"documents": ["test"]}
    response = cast(Dict, send_post_request(url, data))
    dim = len(response["embeddings"][0])
    opensearch.create_index(
        index, db_name, embedding_model, chunk_size, overlap, dim
    )


def main():
    db_name = "llm_demokit_v2"
    index = "1139c161-22d4-4ef1-96ec-94c09055daec"

    create_index(
        index,
        db_name,
        "MULTILINGUAL-E5",
        600,
        180,
    )

    df = pd.read_csv("llm_v2.csv")
    chunks = chunks_to_embedding(df)
    save_chunk_to_db(chunks, index)

    
if __name__ == "__main__":
    main()
