"""Milestone 4a: embed chunks.json and store them in ChromaDB.

Run:  .venv/bin/python index_chunks.py

Two decisions worth knowing about:

1. The text that gets EMBEDDED is the heading breadcrumb plus the chunk text,
   not the chunk text alone. That is the whole point of collecting breadcrumbs
   during chunking: a chunk reading "Things Rora can do for you: ..." embeds as
   "Tech Interview Handbook > Negotiation services > Rora | Things Rora can
   do for you: ...", so the query "what negotiation services exist?" can reach
   it. The raw text is kept separately for display and citation.

2. The collection uses cosine distance. Chroma returns *distance*, and for
   cosine space distance = 1 - cosine_similarity, so query.py converts back.
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
CHUNKS = ROOT / "chunks.json"
DB_DIR = ROOT / "chroma_db"
COLLECTION = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"


def embedding_text(chunk):
    """What actually gets embedded: breadcrumb + text."""
    crumb = chunk.get("heading_path", "").strip()
    return f"{crumb}\n\n{chunk['text']}" if crumb else chunk["text"]


def main():
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))
    print(f"loaded {len(chunks)} chunks from {CHUNKS.name}")

    model = SentenceTransformer(MODEL_NAME)
    texts = [embedding_text(c) for c in chunks]
    print(f"embedding with {MODEL_NAME} ...")
    vectors = model.encode(texts, batch_size=64, show_progress_bar=False,
                           normalize_embeddings=True)
    print(f"  {vectors.shape[0]} vectors of {vectors.shape[1]} dims")

    client = chromadb.PersistentClient(path=str(DB_DIR))
    # rebuild from scratch so re-running never leaves stale chunks behind
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    coll = client.create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"})

    ids = [f"{c['source_id']}-{c['chunk_index']}-{i}" for i, c in enumerate(chunks)]

    # Position of each chunk WITHIN its own source document (0-based), plus the
    # document's total, so a citation can say "chunk 3 of 27 in 07-negotiation".
    # chunk_index alone is not enough: it restarts per markdown section, so the
    # same value recurs many times inside one document.
    per_doc = {}
    for c in chunks:
        per_doc.setdefault(c["source_file"], []).append(c)
    position = {}
    for fname, group in per_doc.items():
        for pos, c in enumerate(group):
            position[id(c)] = (pos, len(group))

    metas = []
    for c in chunks:
        pos, total = position[id(c)]
        metas.append({
            "source_id": str(c.get("source_id", "")),
            "source_title": str(c.get("source_title", "")),
            "source_url": str(c.get("source_url", "")),
            "source_type": str(c.get("source_type", "")),
            "source_file": str(c.get("source_file", "")),
            "heading_path": str(c.get("heading_path", "")),
            "doc_position": pos,          # 0-based position within its document
            "doc_total": total,           # how many chunks that document produced
            "section_index": int(c.get("chunk_index", 0)),
            "chars": len(c["text"]),
        })

    B = 500
    for i in range(0, len(chunks), B):
        coll.add(
            ids=ids[i:i + B],
            embeddings=vectors[i:i + B].tolist(),
            documents=[c["text"] for c in chunks[i:i + B]],
            metadatas=metas[i:i + B],
        )
    print(f"stored {coll.count()} chunks in {DB_DIR.name}/{COLLECTION}")


if __name__ == "__main__":
    main()
