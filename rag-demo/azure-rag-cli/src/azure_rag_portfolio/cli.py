"""Command-line interface for the Azure RAG portfolio."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .create_ndjson import create_ndjson_from_pdf
from .rag import run_rag
from .upload import upload_ndjson


def _default_doc_paths(pdf: Path) -> tuple[Path, Path, Path]:
  stem = pdf.stem
  parent = pdf.parent
  return (
    pdf,
    parent / f"{stem}_chunks.ndjson",
    parent / f"{stem}_chunks_with_embedding.ndjson",
  )


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Azure RAG portfolio: chunk PDFs, upload to AI Search, and query."
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  create_parser = subparsers.add_parser(
    "create", help="Extract PDF text, chunk it, and write NDJSON with embeddings."
  )
  create_parser.add_argument(
    "--pdf",
    type=Path,
    default=Path("sayno_230405.pdf"),
    help="Input PDF file.",
  )
  create_parser.add_argument(
    "--chunks",
    type=Path,
    help="Output NDJSON path for text chunks only.",
  )
  create_parser.add_argument(
    "--embeddings",
    type=Path,
    help="Output NDJSON path for chunks with embeddings.",
  )
  create_parser.add_argument(
    "--doc-id",
    help="Document ID used in chunk records (default: PDF stem, dots removed).",
  )

  upload_parser = subparsers.add_parser(
    "upload", help="Create the search index if needed and upload embedded NDJSON."
  )
  upload_parser.add_argument(
    "--ndjson",
    type=Path,
    default=Path("sayno_230405_chunks_with_embedding.ndjson"),
    help="Embedded NDJSON file to upload.",
  )

  query_parser = subparsers.add_parser(
    "query", help="Run vector search and generate an answer with Azure OpenAI."
  )
  query_parser.add_argument(
    "question",
    nargs="?",
    default="세이노는 누구인가?",
    help="Question to ask.",
  )
  query_parser.add_argument(
    "-k",
    type=int,
    help="Number of chunks to retrieve (overrides VECTOR_SEARCH_K).",
  )
  query_parser.add_argument(
    "--show-results",
    action="store_true",
    help="Print retrieved chunks before the answer.",
  )

  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  try:
    if args.command == "create":
      pdf_path, chunks_path, embeddings_path = _default_doc_paths(args.pdf)
      if args.chunks:
        chunks_path = args.chunks
      if args.embeddings:
        embeddings_path = args.embeddings

      create_ndjson_from_pdf(
        pdf_path,
        chunks_path,
        embeddings_path,
        doc_id=args.doc_id,
      )
      print(f"Wrote chunks: {chunks_path}")
      print(f"Wrote embeddings: {embeddings_path}")

    elif args.command == "upload":
      count = upload_ndjson(args.ndjson)
      print(f"Uploaded {count} documents to index.")

    elif args.command == "query":
      results, answer = run_rag(args.question, k=args.k)
      if args.show_results:
        print("=== Search results ===")
        for doc in results:
          print(doc)
        print("=== Search results ===")
      print(answer)

    else:
      parser.error(f"Unknown command: {args.command}")

  except RuntimeError as exc:
    print(f"Error: {exc}", file=sys.stderr)
    return 1

  return 0
