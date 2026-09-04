"""Milestone 4b: retrieve chunks for a question.

Run:  .venv/bin/python query_index.py "how many leetcode problems should I do?"

Chroma returns cosine DISTANCE; similarity = 1 - distance. Scores on this corpus
run low even for correct matches (a verified question-to-answer pair measured
0.384), so RELEVANCE_FLOOR is deliberately low and is tuned in
test_retrieval.py against the five evaluation questions plus an out-of-scope
control, not guessed.
"""

import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
DB_DIR = ROOT / "chroma_db"
COLLECTION = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 5

# The floor is a CHEAP PRE-FILTER, not the scope decision. Measured on the real
# 868-chunk index over 10 in-domain and 6 out-of-domain questions:
#
#     lowest in-domain    0.451   "Should I take the first offer?"
#     highest out-domain  0.460   "What are good interview questions for a
#                                  nursing job?"
#     window             -0.009   the two bands OVERLAP
#
# So no single cutoff separates in-scope from out-of-scope. A floor tuned to
# admit "Should I take the first offer?" also admits the nursing question; a
# floor tuned to reject the nursing question also rejects a legitimate
# negotiation question. (An earlier value of 0.48, tuned against only the five
# crisp factual evaluation questions, falsely refused "Is grinding LeetCode
# worth the time?" at 0.461.)
#
# 0.35 is therefore set only to reject queries with no plausible relationship to
# the corpus at all --- "What is the capital of Australia?" (0.161), "How do I
# fix a leaking kitchen tap?" (0.185). Everything above it is passed to the LLM,
# which can read the retrieved text and see that software-engineering interview
# advice does not answer a question about nursing. Refusal is a two-stage
# mechanism: this floor, then the grounding prompt.
RELEVANCE_FLOOR = 0.35

# At most this many chunks from any one source document may occupy the top-k.
# Without it, question 3 returned five chunks from the same forum thread, each
# repeating the same prepended opening post --- five slots delivering one
# document's worth of information. Overlap plus the thread policy both duplicate
# text, so near-identical neighbours crowd the results without this cap.
MAX_PER_SOURCE = 2

_model = None
_coll = None


def _load():
    global _model, _coll
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
        client = chromadb.PersistentClient(path=str(DB_DIR))
        _coll = client.get_collection(COLLECTION)
    return _model, _coll


def search(question, k=TOP_K, max_per_source=MAX_PER_SOURCE):
    """Return [{score, text, meta}] best-first, capped per source document.

    Over-fetches so that dropping crowded duplicates still leaves k results.
    Pass max_per_source=None to see raw nearest-neighbour output.
    """
    model, coll = _load()
    qv = model.encode([question], normalize_embeddings=True)
    fetch = k if max_per_source is None else min(k * 6, 200)
    res = coll.query(query_embeddings=qv.tolist(), n_results=fetch,
                     include=["documents", "metadatas", "distances"])
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0],
                               res["distances"][0]):
        hits.append({"score": 1.0 - dist, "text": doc, "meta": meta})
    if max_per_source is None:
        return hits[:k]
    seen, out = {}, []
    for h in hits:
        src = h["meta"]["source_file"]
        if seen.get(src, 0) >= max_per_source:
            continue
        seen[src] = seen.get(src, 0) + 1
        out.append(h)
        if len(out) == k:
            break
    return out


def search_filtered(question, k=TOP_K, floor=RELEVANCE_FLOOR):
    """Same as search(), but drops anything below the relevance floor.

    An empty list means the question is out of scope for this corpus --- this is
    the mechanism behind refusal, not the prompt.
    """
    return [h for h in search(question, k) if h["score"] >= floor]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    question = " ".join(sys.argv[1:])
    hits = search(question)
    print(f"\nquery: {question!r}")
    print(f"floor: {RELEVANCE_FLOOR}   top-k: {TOP_K}\n")
    for i, h in enumerate(hits, 1):
        keep = "KEEP  " if h["score"] >= RELEVANCE_FLOOR else "below "
        m = h["meta"]
        print(f"{keep}#{i}  score {h['score']:.3f}  [{m['source_type']}] "
              f"{m['source_file']}")
        print(f"        {m['heading_path'][:88]}")
        print(f"        {' '.join(h['text'].split())[:180]}")
        print()
    kept = sum(1 for h in hits if h["score"] >= RELEVANCE_FLOOR)
    if kept == 0:
        print("=> nothing above the floor: this question is out of scope.")


if __name__ == "__main__":
    main()
