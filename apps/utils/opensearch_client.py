from typing import Any, Dict, List, Literal

from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_mapping(
    dim: int,
    db_name: str,
    embedding_model: str,
    chunk_size: int,
    overlap: int,
    tags: List[str] | None = None,
    space_type: str = "cosinesimil",
    engine: str = "nmslib",
    ef_search: int = 512,
    ef_construction: int = 512,
    m: int = 16,
    is_alter: bool = False
):
    if tags is None:
        tags = ["llm_LAB"]
    return {
        "settings": {
            "index": {"knn": True, "knn.algo_param.ef_search": ef_search}
        },
        "mappings": {
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": space_type,
                        "engine": engine,
                        "parameters": {
                            "ef_construction": ef_construction,
                            "m": m,
                        },
                    },
                }
            },
            "_meta": {
                "embedding_model": embedding_model,
                "chunk_size": chunk_size,
                "overlap": overlap,
                "tags": tags,
                "db_name": db_name,
                "updated": 1 if is_alter else 0
            },
        },
    }


class OpenSearchClient:
    def __init__(self, host: str, port: int = 9200):
        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
        )
        self.query_supported_map = {
            "match",
            "term",
            "wildcard",
            "prefix",
            "regexp",
            "match_all",
        }

    def create_index(
        self,
        index_name: str,
        db_name: str,
        embedding_model: str,
        chunk_size: int,
        overlap: int,
        dim: int,
        tags: List[str] | None = None,
        is_alter: bool = False
    ):
        if self.is_db_name_exists(db_name, tags):
            raise ValueError(f"Database '{db_name}' already exists.")
        mapping = get_mapping(
            dim, db_name, embedding_model, chunk_size, 
            overlap, is_alter=is_alter, tags=tags
        )
        self.client.indices.create(index=index_name, body=mapping)

    def query_index(
        self,
        index: str,
        query_type: Literal[
            "match", "term", "wildcard", "prefix", "regexp", "match_all"
        ],
        query_params: Dict[str, Any] | None = None,
        size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        General query function to search an OpenSearch index based on the
        given query type and parameters.

        :param index: Name of the OpenSearch index to query.
        :param query_type: Type of query, e.g., 'match', 'term', 'wildcard',
        'prefix', 'regexp', 'match_all'.
        :param query_params: Query parameters in the format { "field": "value"\
              } for 'match', 'term', 'wildcard', 'prefix', and 'regexp' \
                queries, or an empty dictionary for 'match_all'.
        :param size: Number of results to return (default is 10).
        :return: A list of query results, each represented as a dictionary.
        """
        if query_type not in self.query_supported_map:
            raise ValueError(f"Unsupported query type: {query_type}")

        if query_params is None:
            query_params = {}

        # Construct the query body
        query = {"query": {query_type: query_params}}

        if query_type == "match_all":
            size = self.get_index_count(index)

        # Execute the query with the specified size
        response = self.client.search(index=index, body=query, size=size)

        # Return the results
        results = [
            {"_id": hit["_id"], "_source": hit["_source"]}
            for hit in response["hits"]["hits"]
        ]
        return results

    def is_index_exists(self, index_name: str):
        return self.client.indices.exists(index=index_name)

    def is_db_name_exists(self, db_name: str, tags: List[str] | None = None):
        mappings = self.client.indices.get_mapping()
        for _, mapping in mappings.items():
            if (
                "_meta" in mapping["mappings"]
                and "db_name" in mapping["mappings"]["_meta"]
                and mapping["mappings"]["_meta"]["db_name"] == db_name
            ):
                if tags:
                    if "tags" in mapping["mappings"]["_meta"] and set(
                        tags
                    ) == set(mapping["mappings"]["_meta"]["tags"]):
                        return True
                else:
                    return True
        return False
    
    def get_db_name(self, index_name: str) -> str | None:
        if self.is_index_exists(index_name):
            mappings = self.client.indices.get_mapping()
            mapping = mappings[index_name]
            if (
                "_meta" in mapping["mappings"]
                and "db_name" in mapping["mappings"]["_meta"]
            ):
                return mapping["mappings"]["_meta"]["db_name"]
            return ""
        else:
            return None
        
    def get_mapping_info(self, index_name: str) -> Dict[str, Any]:
        if self.is_index_exists(index_name):
            mappings = self.client.indices.get_mapping()
            return mappings[index_name]
        else:
            return {}
        
    def get_index_count(self, index_name: str):
        return self.client.count(index=index_name)["count"]

    def add_documents(self, index_name: str, documents: List[Dict[str, Any]]):
        """
        add documents to the specified index.

        :param index_name: Name of the OpenSearch index.
        :param documents: List of documents to add, each represented as a \
        dictionary.
        """

        actions = [
            {
                "_index": index_name,
                "_source": {
                    "vector_field": doc["vector_field"],
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                },
            }
            for doc in documents
        ]
        success, failed = bulk(self.client, actions)

        if failed:
            raise ValueError(f"Failed to add documents: {failed}")

        # Refresh the index to make documents searchable immediately
        self.client.indices.refresh(index=index_name)

    def search(self, index_name: str, query: dict):
        return self.client.search(index=index_name, body=query)

    def delete_index(self, index_name: str):
        self.client.indices.delete(index=index_name)

    def get_index_with_tag(self, tag: str):
        mappings = self.client.indices.get_mapping()
        index = {}
        for index_name, mapping in mappings.items():
            if (
                "_meta" in mapping["mappings"]
                and "tags" in mapping["mappings"]["_meta"]
                and tag in mapping["mappings"]["_meta"]["tags"]
            ):
                index[mapping["mappings"]["_meta"]["db_name"]] = index_name
        return index
