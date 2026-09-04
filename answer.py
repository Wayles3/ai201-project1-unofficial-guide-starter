"""Milestone 5: grounded generation over the retrieved chunks.

Run:  .venv/bin/python answer.py "how many leetcode problems should I do?"

Grounding is enforced in three places, not one:

  1. RETRIEVAL FLOOR (query_index.RELEVANCE_FLOOR = 0.35) --- if nothing clears
     it, the LLM is never called at all. Deterministic, no prompt involved.
  2. CONTEXT STRUCTURE --- sources are numbered, labelled with type and fetch
     date, and separated by explicit delimiters, so the model can cite a
     specific source and can see when two sources disagree.
  3. SYSTEM PROMPT --- the instruction below. This is the only stage that can
     reject an adjacent-domain question (e.g. nursing interviews), because
     deciding that requires reading the text, which cosine distance cannot do.
"""

import os
import sys
import textwrap

from dotenv import load_dotenv
from groq import Groq

from query_index import MAX_PER_SOURCE, RELEVANCE_FLOOR, TOP_K, search

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """\
You are a research assistant answering questions about software engineering \
interview preparation. You answer ONLY from the numbered SOURCES supplied in \
the user message. You have no other knowledge available to you for this task.

Rules, in order of priority:

1. GROUND EVERY CLAIM. After each factual statement, cite the source it came \
from as [S1], [S2], etc. A statement with no citation is not allowed. Never \
cite a source number that does not appear in the SOURCES block.

2. REFUSE WHEN THE SOURCES DO NOT ANSWER THE QUESTION. If the sources are \
about a different subject than the question asks about, say exactly what you \
do and do not have, in this form: "My sources don't cover this. They discuss \
<what they actually discuss>, not <what was asked>." Do not answer from \
general knowledge. This applies even when the sources are on an adjacent \
topic that shares vocabulary with the question -- for example, sources about \
software engineering interviews do not answer a question about nursing \
interviews, and sources about salary negotiation do not answer a question \
about mortgage or rent negotiation.

3. REPORT DISAGREEMENT, DO NOT RESOLVE IT. If two sources conflict, say so and \
attribute each position: "[S1] says X, while [S3] says the opposite." Do not \
average them, and do not silently pick the one you find more plausible.

4. DO NOT GENERALISE FROM A NARROWER SOURCE. If a source is one person's \
account, attribute it to that person or that post rather than stating it as a \
general fact. If the question names a specific company and the sources discuss \
interviewing generally, say the sources do not cover that company \
specifically, even if they are otherwise on-topic.

5. FLAG AGE WHEN IT MATTERS. Each source carries a fetch date and some carry \
their own dates. If a claim concerns something that changes over time \
(hiring process, market conditions, tooling), mention how old the source is.

6. QUOTE NUMBERS EXACTLY as they appear. Do not round, convert or recompute \
them.

Be concise. Two or three short paragraphs at most."""


def build_context(hits):
    """Number the retrieved chunks and label them for citation."""
    blocks = []
    for i, h in enumerate(hits, 1):
        m = h["meta"]
        crumb = m.get("heading_path", "")
        blocks.append(
            f"[S{i}]\n"
            f"source_file: {m['source_file']}\n"
            f"title: {m['source_title']}\n"
            f"type: {m['source_type']}   fetched: {m.get('fetched', 'see documents/')}\n"
            f"section: {crumb}\n"
            f"url: {m['source_url']}\n"
            f"similarity: {h['score']:.3f}\n"
            f"---\n{h['text']}"
        )
    return "\n\n========\n\n".join(blocks)


def answer(question, k=TOP_K, floor=RELEVANCE_FLOOR, model=MODEL):
    """Retrieve, then generate a grounded answer. Returns a dict."""
    hits = search(question, k, MAX_PER_SOURCE)
    kept = [h for h in hits if h["score"] >= floor]

    if not kept:
        best = max((h["score"] for h in hits), default=0.0)
        return {
            "question": question,
            "refused_at": "retrieval",
            "answer": ("My sources don't cover this. Nothing in the corpus came "
                       f"close enough to the question (best similarity "
                       f"{best:.3f}, floor {floor})."),
            "hits": hits,
            "kept": [],
        }

    context = build_context(kept)
    user = (f"SOURCES\n\n{context}\n\n========\n\n"
            f"QUESTION: {question}\n\n"
            f"Answer using only the sources above, citing [S1]-[S{len(kept)}].")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": user}],
        temperature=0.0,
        max_tokens=700,
    )
    return {
        "question": question,
        "refused_at": None,
        "answer": resp.choices[0].message.content.strip(),
        "hits": hits,
        "kept": kept,
    }


def format_sources(kept):
    lines = []
    for i, h in enumerate(kept, 1):
        m = h["meta"]
        lines.append(f"[S{i}] {m['source_title']}  "
                     f"({m['source_type']}, sim {h['score']:.3f})\n"
                     f"      {m['source_file']} "
                     f"chunk {m.get('doc_position', '?')}/{m.get('doc_total', '?')}\n"
                     f"      {m['source_url']}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    q = " ".join(sys.argv[1:])
    res = answer(q)
    print(f"\nQUESTION: {q}\n")
    print("ANSWER")
    print(textwrap.indent(res["answer"], "  "))
    if res["kept"]:
        print("\nSOURCES")
        print(format_sources(res["kept"]))
    else:
        print(f"\n(refused at {res['refused_at']}; no sources passed the floor)")


if __name__ == "__main__":
    main()
