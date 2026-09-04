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

2. REFUSE ONLY WHEN THE SOURCES ARE ABOUT A DIFFERENT SUBJECT, not merely a \
narrower one. Refuse (say exactly what you do and do not have, in this form: \
"My sources don't cover this. They discuss <what they actually discuss>, not \
<what was asked>.") when the sources are about a genuinely different topic \
that happens to share vocabulary with the question -- sources about software \
engineering interviews do not answer a question about nursing interviews, and \
sources about salary negotiation do not answer a question about mortgage or \
rent negotiation. Do NOT refuse when the sources are on the exact same \
subject as the question but do not name a specific company, give an exact \
number, or use the question's exact wording -- ANSWER using what the sources \
say, and say plainly that they don't speak to that specific company/number if \
that's true. Example: "How do I prepare for a Google interview?" with sources \
that give general software-engineering interview prep advice (not Google- \
specific) should be ANSWERED using that general advice, with a note that the \
sources are general rather than Google-specific -- it should NOT be refused. \
Example: "How long does the hiring process take?" with sources that mention \
a 3-month prep recommendation and interview-length data should be ANSWERED \
with those figures, explicitly framed as partial, not refused for lacking one \
single "total process length" number. Never answer from knowledge outside the \
sources, but do synthesize and hedge rather than refuse whenever the sources \
are actually on-topic.

3. REPORT DISAGREEMENT, DO NOT RESOLVE IT. If two sources conflict, say so and \
attribute each position: "[S1] says X, while [S3] says the opposite." Do not \
average them, and do not silently pick the one you find more plausible.

4. DO NOT MISREPRESENT WHAT A SOURCE IS ABOUT. If a source is one person's \
account, attribute it to that person or that post rather than stating it as a \
general fact. If the question names a specific company and a retrieved \
chunk is from a thread ABOUT that company but the chunk's own text does not \
actually discuss that company (e.g. a generic reply inside a company-named \
thread), say plainly that the reply itself does not address that company, \
rather than presenting it as if it does. This is different from rule 2: it is \
about not overstating what an otherwise-relevant, on-topic chunk actually \
says, not about refusing on-topic questions.

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
