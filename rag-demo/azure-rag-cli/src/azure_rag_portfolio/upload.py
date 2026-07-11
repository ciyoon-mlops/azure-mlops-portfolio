"""Upload embedded NDJSON documents to Azure AI Search."""

from __future__ import annotations

import json
from pathlib import Path

import requests

from .settings import Settings


def load_ndjson(path: Path) -> list[dict]:
  docs: list[dict] = []
  with path.open("r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if line:
        docs.append(json.loads(line))
  return docs


def _index_schema(settings: Settings) -> dict:
  index_name = settings.azure_search_index
  return {
    "name": index_name,
    "fields": [
      {"name": "id", "type": "Edm.String", "key": True},
      {"name": "parent_id", "type": "Edm.String", "filterable": True},
      {"name": "content", "type": "Edm.String", "searchable": True},
      {
        "name": "embedding",
        "type": "Collection(Edm.Single)",
        "searchable": True,
        "dimensions": settings.embedding_dimensions,
        "vectorSearchProfile": "vprofile",
      },
    ],
    "vectorSearch": {
      "profiles": [{"name": "vprofile", "algorithm": "vconfig"}],
      "algorithms": [{"name": "vconfig", "kind": "hnsw"}],
    },
  }


def ensure_index(settings: Settings) -> None:
  api_version = settings.azure_search_api_version
  base = settings.search_endpoint
  headers = {"api-key": settings.azure_search_admin_key}

  list_url = f"{base}/indexes?api-version={api_version}"
  resp = requests.get(list_url, headers=headers, timeout=60)
  resp.raise_for_status()
  indexes = [item["name"] for item in resp.json().get("value", [])]

  if settings.azure_search_index in indexes:
    return

  create_url = (
    f"{base}/indexes/{settings.azure_search_index}?api-version={api_version}"
  )
  resp = requests.put(
    create_url,
    headers={**headers, "Content-Type": "application/json"},
    json=_index_schema(settings),
    timeout=60,
  )
  resp.raise_for_status()


def upload_ndjson(
  ndjson_path: Path,
  *,
  settings: Settings | None = None,
) -> int:
  """Create the index if needed and upload documents. Returns document count."""
  settings = settings or Settings.from_env()
  docs = load_ndjson(ndjson_path)

  ensure_index(settings)

  api_version = settings.azure_search_api_version
  url = (
    f"{settings.search_endpoint}/indexes/{settings.azure_search_index}"
    f"/docs/index?api-version={api_version}"
  )
  headers = {
    "Content-Type": "application/json",
    "api-key": settings.azure_search_admin_key,
  }
  resp = requests.post(url, headers=headers, json={"value": docs}, timeout=120)
  resp.raise_for_status()
  return len(docs)
