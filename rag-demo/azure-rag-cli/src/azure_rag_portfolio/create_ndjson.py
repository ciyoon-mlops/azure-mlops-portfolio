"""PDF chunking and embedding for Azure AI Search."""

from __future__ import annotations

import json
from pathlib import Path

import fitz
from openai import AzureOpenAI

from .settings import Settings


def chunk_text(text: str, max_length: int) -> list[str]:
  chunks: list[str] = []
  start = 0
  while start < len(text):
    end = min(start + max_length, len(text))
    chunks.append(text[start:end])
    start = end
  return chunks


def extract_pdf_text(pdf_path: Path) -> str:
  doc = fitz.open(pdf_path)
  try:
    return "".join(page.get_text() for page in doc)
  finally:
    doc.close()


def write_chunks_ndjson(
  chunks: list[str],
  output_path: Path,
  *,
  doc_id: str,
) -> None:
  output_path.parent.mkdir(parents=True, exist_ok=True)
  with output_path.open("w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks):
      record = {
        "id": f"{doc_id}_chunk_{i}",
        "parent_id": doc_id,
        "content": chunk,
      }
      f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_embeddings_ndjson(
  chunks: list[str],
  output_path: Path,
  *,
  doc_id: str,
  client: AzureOpenAI,
  embedding_deployment: str,
) -> None:
  output_path.parent.mkdir(parents=True, exist_ok=True)
  with output_path.open("w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks):
      response = client.embeddings.create(
        model=embedding_deployment,
        input=chunk,
      )
      record = {
        "id": f"{doc_id}_chunk_{i}",
        "parent_id": doc_id,
        "content": chunk,
        "embedding": response.data[0].embedding,
      }
      f.write(json.dumps(record, ensure_ascii=False) + "\n")


def create_ndjson_from_pdf(
  pdf_path: Path,
  chunks_path: Path,
  embeddings_path: Path,
  *,
  doc_id: str | None = None,
  settings: Settings | None = None,
) -> tuple[Path, Path]:
  """Extract a PDF, write chunk and embedding NDJSON files."""
  settings = settings or Settings.from_env()
  doc_id = doc_id or pdf_path.stem.replace(".", "_")

  text = extract_pdf_text(pdf_path)
  chunks = chunk_text(text, settings.chunk_max_length)

  write_chunks_ndjson(chunks, chunks_path, doc_id=doc_id)

  client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint,
  )
  write_embeddings_ndjson(
    chunks,
    embeddings_path,
    doc_id=doc_id,
    client=client,
    embedding_deployment=settings.azure_openai_embedding_deployment,
  )

  return chunks_path, embeddings_path
