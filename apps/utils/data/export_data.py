
import logging
from typing import Dict, List

from utils.opensearch_client import OpenSearchClient


def get_data(
    client: OpenSearchClient, index: str, size: int | None = None
) -> List[Dict[str, List[str] | str]]:
    logging.debug("get_data: index=%s", index)

    if size:
        data: List[Dict[str, List[str] | str]] = client.query_index(
            index=index, query_type="match_all", size=size)
    else:
        data: List[Dict[str, List[str] | str]] = client.query_index(
            index=index, query_type="match_all")

    response = [
        {
            "Chunk Id": _data["_id"],
            "Text": _data["_source"]["text"],
            "Metadata": _data["_source"]["metadata"],
            "Source": _data["_source"]["metadata"]["source_file"],
        } 
        for _data in data
    ]
    return response