"""Vector search and chat completion for RAG queries."""

from __future__ import annotations

import requests
from openai import AzureOpenAI, NotFoundError

from .settings import Settings


def embed_query(client: AzureOpenAI, query: str, deployment: str) -> list[float]:
  response = client.embeddings.create(model=deployment, input=query)
  return response.data[0].embedding


def vector_search(
  query_embedding: list[float],
  *,
  settings: Settings,
  k: int | None = None,
) -> list[dict]:
  k = k or settings.vector_search_k
  api_version = settings.azure_search_api_version
  url = (
    f"{settings.search_endpoint}/indexes/{settings.azure_search_index}"
    f"/docs/search?api-version={api_version}"
  )
  headers = {
    "api-key": settings.azure_search_admin_key,
    "Content-Type": "application/json",
  }
  body = {
    "vectorQueries": [
      {
        "kind": "vector",
        "vector": query_embedding,
        "fields": "embedding",
        "k": k,
      }
    ],
    "select": "id,parent_id,content",
  }
  resp = requests.post(url, headers=headers, json=body, timeout=60)
  if not resp.ok:
    raise RuntimeError(f"Search failed ({resp.status_code}): {resp.text}")

  payload = resp.json()
  if "value" not in payload:
    raise RuntimeError(f"Search API error: {payload}")
  return payload["value"]


def answer_with_context(
  client: AzureOpenAI,
  query: str,
  context_docs: list[dict],
  *,
  chat_deployment: str,
) -> str:
  context = "\n".join(doc["content"] for doc in context_docs)
  try:
    completion = client.chat.completions.create(
      model=chat_deployment,
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
          "role": "user",
          "content": f"질문: {query}\n\n검색된 문서:\n{context}",
        },
      ],
    )
  except NotFoundError as exc:
    raise RuntimeError(
      "Azure OpenAI chat deployment was not found. "
      "Set AZURE_OPENAI_CHAT_DEPLOYMENT to your actual Azure deployment name "
      f"(current value: {chat_deployment!r})."
    ) from exc
  return completion.choices[0].message.content or ""


def run_rag(
  query: str,
  *,
  settings: Settings | None = None,
  k: int | None = None,
) -> tuple[list[dict], str]:
  """Run vector search and return (search results, LLM answer)."""
  settings = settings or Settings.from_env()

  client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint,
  )

  embedding = embed_query(
    client, query, settings.azure_openai_embedding_deployment
  )
  results = vector_search(embedding, settings=settings, k=k)
  answer = answer_with_context(
    client,
    query,
    results,
    chat_deployment=settings.azure_openai_chat_deployment,
  )
  return results, answer
