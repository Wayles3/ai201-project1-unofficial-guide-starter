"""Milestone 6: run the evaluation plan end to end and print it for the README.

Run:  .venv/bin/python run_eval.py
"""

from answer import answer
from query_index import RELEVANCE_FLOOR, TOP_K

# (question, expected answer, the phrase that must appear for the answer to be right)
EVAL = [
    ("How many LeetCode problems did someone solve before passing a FAANG interview, "
     "and what was the difficulty split?",
     "175 total: 52 easy, 106 medium, 17 hard (Marchenko, amarchenko.dev, Jan 2024)",
     "175"),
    ("What share of recruiting leaders are conducting interviews in person to combat "
     "candidate fraud?",
     "72.4% (Gartner survey, via Computerworld)",
     "72.4"),
    ("How difficult are the LeetCode questions in entry-level interviews, and do "
     "interviewers give hints?",
     "Mostly mediums; interviewers usually guide you or give a hint if you explain "
     "your thought process",
     "medium"),
    ("Is the first offer a company gives the best package they can offer?",
     "No -- the initial offer is never the best package; recruiters expect negotiation",
     "never"),
    ("How much more often do women abandon interview practice than men after a single "
     "bad interview?",
     "7 times more often (interviewing.io)",
     "7"),
]

# Questions that SHOULD be refused, and which stage should catch each one.
REFUSALS = [
    ("What is the best way to negotiate a mortgage rate?", "prompt (adjacent domain)"),
    ("What are good interview questions for a nursing job?", "prompt (adjacent domain)"),
    ("What is the capital of Australia?", "retrieval floor"),
]

# The known corpus trap: this thread names three companies and none of its
# replies mentions any of them.
TRAPS = [
    ("What was the Expedia new grad software engineer interview like?",
     "Sources name Expedia in a thread title but no reply discusses Expedia, so the "
     "correct behaviour is to say the sources do not cover it."),
]


def show(res, label=""):
    print(f"\n{'-' * 78}")
    print(f"Q{label}: {res['question']}")
    print(f"{'-' * 78}")
    if res["refused_at"]:
        print(f"[refused at {res['refused_at']}]")
    print(res["answer"])
    if res["kept"]:
        srcs = ", ".join(f"S{i}={h['meta']['source_file']}"
                         for i, h in enumerate(res["kept"], 1))
        print(f"\nsources given to model: {srcs}")
        print(f"top similarity: {res['kept'][0]['score']:.3f}  "
              f"(distance {1 - res['kept'][0]['score']:.3f})")


def main():
    print("=" * 78)
    print(f"EVALUATION RUN   top_k={TOP_K}   floor={RELEVANCE_FLOOR}")
    print("=" * 78)

    print("\n\n##### PART 1: the five evaluation questions #####")
    verdicts = []
    for i, (q, expected, must) in enumerate(EVAL, 1):
        res = answer(q)
        show(res, str(i))
        got = must.lower() in res["answer"].lower()
        print(f"\nexpected: {expected}")
        print(f"contains {must!r}: {'YES' if got else 'NO'}")
        verdicts.append((i, got))

    print("\n\n##### PART 2: refusals #####")
    for q, where in REFUSALS:
        res = answer(q)
        show(res)
        print(f"\nshould be caught by: {where}")

    print("\n\n##### PART 3: the attribution trap #####")
    for q, note in TRAPS:
        res = answer(q)
        show(res)
        print(f"\ncorrect behaviour: {note}")

    print("\n\n" + "=" * 78)
    ok = sum(1 for _, g in verdicts if g)
    print(f"expected-phrase check: {ok}/{len(EVAL)}")
    print("=" * 78)


if __name__ == "__main__":
    main()
