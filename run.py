import argparse
import os
from pathlib import Path
from pageindex import PageIndexClient
from pageindex.errors import PageIndexAPIError


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question",
        nargs="?",
        default="What company and reporting year does this document cover?",
    )
    args = parser.parse_args(argv)
    project_dir = Path(__file__).resolve().parent

    os.environ["OPENAI_API_KEY"] = "ollama"
    for variable in ("NO_PROXY", "no_proxy"):
        os.environ[variable] = ",".join(
            filter(None, (os.environ.get(variable), "localhost", "127.0.0.1", "::1"))
        )

    client = PageIndexClient(
        index_model="openai/gemma4:e4b-4k",
        chat_model="openai/gemma4:e4b-4k",
        index_backend={
            "api_base": "http://localhost:11434/v1",
            "api_key": "ollama",
        },
        chat_backend={
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
        },
        summary_concurrency=1,
        storage_path=project_dir / ".pageindex",
    )

    pdf = (
        project_dir
        / "examples/documents/2023-annual-report-truncated.pdf"
    )
    try:
        doc_id = client.get_document_id(pdf.name)
    except PageIndexAPIError:
        print(f"Indexing: {pdf.name}", flush=True)
        doc_id = client.submit_document(str(pdf))["doc_id"]
        print(f"Index ready: {doc_id}", flush=True)
    else:
        print(f"Using saved index: {doc_id}", flush=True)

    answer = client.chat(
        args.question,
        doc_id=doc_id,
    )
    print(answer)


if __name__ == "__main__":
    main()