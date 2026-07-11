"""Load configuration from environment variables and optional .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    # rag-demo/azure-rag-cli/.env (package lives under src/)
    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    load_dotenv(_PROJECT_ROOT / ".env")
except ImportError:
    pass


def _require(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


@dataclass(frozen=True)
class Settings:
  azure_openai_api_key: str
  azure_openai_endpoint: str
  azure_openai_api_version: str
  azure_openai_embedding_deployment: str
  azure_openai_chat_deployment: str
  azure_search_service: str
  azure_search_admin_key: str
  azure_search_index: str
  embedding_dimensions: int
  chunk_max_length: int
  vector_search_k: int
  azure_search_api_version: str

  @classmethod
  def from_env(cls) -> Settings:
    return cls(
      azure_openai_api_key=_require("AZURE_OPENAI_API_KEY"),
      azure_openai_endpoint=_require("AZURE_OPENAI_API_ENDPOINT"),
      azure_openai_api_version=os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
      ),
      azure_openai_embedding_deployment=os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"
      ),
      azure_openai_chat_deployment=os.getenv(
        "AZURE_OPENAI_CHAT_DEPLOYMENT", "o4-mini"
      ),
      azure_search_service=_require("AZURE_SEARCH_SERVICE"),
      azure_search_admin_key=_require("AZURE_SEARCH_ADMIN_KEY"),
      azure_search_index=os.getenv("AZURE_SEARCH_INDEX", "idx-docs"),
      embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "3072")),
      chunk_max_length=int(os.getenv("CHUNK_MAX_LENGTH", "1000")),
      vector_search_k=int(os.getenv("VECTOR_SEARCH_K", "3")),
      azure_search_api_version=os.getenv(
        "AZURE_SEARCH_API_VERSION", "2023-11-01"
      ),
    )

  @property
  def search_endpoint(self) -> str:
    return f"https://{self.azure_search_service}.search.windows.net"
