"""Milestone 4c: does retrieval actually find the answers? Run BEFORE any LLM.

Run:  .venv/bin/python test_retrieval.py

Each evaluation question from planning.md names the document its verified answer
lives in, and a phrase that must appear in the retrieved text. That makes this a
lookup rather than a judgement call: either the chunk carrying the answer is in
the top-k or it is not.

Testing retrieval separately from generation matters because "wrong answer from
correct chunks" and "wrong answer because the chunk was never retrieved" are
different bugs with different fixes.
"""

from query_index import RELEVANCE_FLOOR, TOP_K, search

# (question, expected source file prefix, phrase that must appear in the chunk)
CASES = [
    ("How many LeetCode problems did someone solve before passing a FAANG interview?",
     "16-marchenko", "175 LeetCode"),
    ("What share of recruiting leaders are conducting interviews in person to combat fraud?",
     "17-computerworld", "72.4%"),
    ("How difficult are the LeetCode questions for entry level roles, and do interviewers give hints?",
     "18-levels-newgrad-expedia", "mediums"),
    ("Is the first offer a company gives the best package they can offer?",
     "07-negotiation", "never the best package"),
    ("How much more often do women quit interview practice than men after a bad interview?",
     "13-iio-practice-gap", "7 times"),
]

# Out-of-scope controls, hardest first. The first three are *adjacent* domains
# that share vocabulary with the corpus, which is what makes them hard; the last
# two are unrelated and should be rejected by the floor alone.
OUT_OF_SCOPE = [
    "What are good interview questions for a nursing job?",
    "What is the best way to negotiate a mortgage rate?",
    "How do I negotiate rent with my landlord?",
    "How do I prepare for the LSAT?",
    "What is the capital of Australia?",
    "How do I fix a leaking kitchen tap?",
]

# In-domain questions phrased abstractly rather than as fact lookups. These are
# the ones a too-high floor falsely refuses, so they belong in the test.
IN_DOMAIN_ABSTRACT = [
    "Is grinding LeetCode worth the time?",
    "Should I take the first offer?",
    "Are take-home assignments common?",
    "How has AI changed technical interviews?",
    "What makes a good answer in a system design interview?",
]

DISAGREEMENT = "Is grinding LeetCode worth the time?"


def main():
    print("=" * 78)
    print(f"RETRIEVAL TEST   top_k={TOP_K}   floor={RELEVANCE_FLOOR}")
    print("=" * 78)

    passed = 0
    for i, (question, want_file, want_phrase) in enumerate(CASES, 1):
        hits = search(question, TOP_K)
        rank_file = next((r for r, h in enumerate(hits, 1)
                          if h["meta"]["source_file"].startswith(want_file)), None)
        rank_phrase = next((r for r, h in enumerate(hits, 1)
                            if want_phrase.lower() in h["text"].lower()), None)
        ok = rank_phrase is not None
        passed += ok
        print(f"\nQ{i}: {question}")
        print(f"  want: {want_file}*  containing {want_phrase!r}")
        print(f"  {'PASS' if ok else 'FAIL'}  "
              f"phrase at rank {rank_phrase}, source file at rank {rank_file}")
        top_dist = 1.0 - hits[0]["score"]
        flag = "OK" if top_dist < 0.5 else "WEAK MATCH (>0.5)"
        print(f"  top-1 distance: {top_dist:.3f}  [{flag}]   "
              f"distances: {[round(1 - h['score'], 3) for h in hits]}")
        for r, h in enumerate(hits, 1):
            mark = "<<<" if (rank_phrase == r) else "   "
            print(f"    {mark} #{r} dist={1 - h['score']:.3f} sim={h['score']:.3f} "
                  f"{h['meta']['source_file'][:32]:32} "
                  f"pos {h['meta'].get('doc_position', '?')}"
                  f"/{h['meta'].get('doc_total', '?')} "
                  f"{' '.join(h['text'].split())[:56]}")

    print("\n" + "=" * 78)
    print(f"IN-SCOPE: {passed}/{len(CASES)} questions retrieved their verified answer")
    print("=" * 78)

    def best(q):
        return max(h["score"] for h in search(q, TOP_K))

    print("\nIN-DOMAIN, ABSTRACTLY PHRASED (must stay ABOVE the floor)")
    for q in IN_DOMAIN_ABSTRACT:
        s = best(q)
        print(f"  {'ok      ' if s >= RELEVANCE_FLOOR else 'REFUSED!'} "
              f"best={s:.3f}  {q}")

    print("\nOUT-OF-SCOPE CONTROLS (floor stage --- adjacent domains are "
          "expected to pass here and be caught by the grounding prompt)")
    for q in OUT_OF_SCOPE:
        s = best(q)
        above = [h for h in search(q, TOP_K) if h["score"] >= RELEVANCE_FLOOR]
        verdict = "floor rejects" if not above else f"passes floor ({len(above)})"
        print(f"  {verdict:18} best={s:.3f}  {q}")

    print("\nSEPARATION CHECK --- can ONE threshold separate in from out?")
    in_all = [(best(q), q) for q in [c[0] for c in CASES] + IN_DOMAIN_ABSTRACT]
    out_all = [(best(q), q) for q in OUT_OF_SCOPE]
    lo, lo_q = min(in_all)
    hi, hi_q = max(out_all)
    print(f"  lowest in-domain   : {lo:.3f}  {lo_q}")
    print(f"  highest out-domain : {hi:.3f}  {hi_q}")
    gap = lo - hi
    print(f"  usable window      : {gap:+.3f}")
    if gap <= 0:
        print("  => NO single floor separates them. Score thresholding alone")
        print("     cannot decide scope; the grounding prompt must do it by")
        print("     reading whether the retrieved text answers the question.")

    print("\nDISAGREEMENT PROBE (corpus answers this both ways)")
    for h in search(DISAGREEMENT, TOP_K):
        print(f"  {h['score']:.3f} {h['meta']['source_file'][:32]:32} "
              f"{' '.join(h['text'].split())[:78]}")


if __name__ == "__main__":
    main()
