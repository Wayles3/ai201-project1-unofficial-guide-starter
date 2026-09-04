"""Measurements behind the Retrieval Approach section of planning.md.

Run: .venv/bin/python scratch/embed_demo.py
"""

from sentence_transformers import SentenceTransformer, util

m = SentenceTransformer("all-MiniLM-L6-v2")

print("=" * 70)
print("PART 1: what a sentence turns into")
print("=" * 70)
v = m.encode("I solved 175 LeetCode problems.")
print("shape:", v.shape)
print("first 8 numbers:", [round(float(x), 4) for x in v[:8]])

print()
print("=" * 70)
print("PART 2: matching a question to its answer with NO shared words")
print("=" * 70)
query = "how much practice is enough before applying?"
chunks = [
    "I solved 175 LeetCode problems: 52 easy, 106 medium, 17 hard.",
    "I studied for coding interview for an entire year.",
    "Most leetcode style questions are usually mediums.",
    "The average technical score across all users is 2.85 out of 4.",
    "Don't feel obligated to accept your offer right away; negotiation is a dialogue.",
]
qv, cv = m.encode(query), m.encode(chunks)
scores = util.cos_sim(qv, cv)[0]
print(f"query: {query!r}\n")
for s, c in sorted(zip(scores.tolist(), chunks), reverse=True):
    shared = (set(query.lower().replace("?", "").split())
              & set(c.lower().replace(".", "").replace(";", "").split())) - {
        "a", "the", "is", "for", "of", "an"}
    print(f"  {s:+.3f}  shared words: {sorted(shared) or 'NONE'}\n          {c}")

print()
print("=" * 70)
print("PART 3: where embeddings BREAK (failure-case material)")
print("=" * 70)
pairs = [
    ("negation",
     "The interviewers give hints when you get stuck.",
     "The interviewers do not give hints when you get stuck."),
    ("domain jargon vs plain English",
     "What level is an E5 at Meta?",
     "What is the senior software engineer level at Meta?"),
    ("jargon the model never learned",
     "Is Blind 75 enough preparation?",
     "Is a curated list of 75 practice problems enough preparation?"),
    ("opposite advice, same topic",
     "Grinding LeetCode is absolutely worth your time.",
     "Grinding LeetCode is a waste of your time."),
]
for label, a, b in pairs:
    s = float(util.cos_sim(m.encode(a), m.encode(b))[0][0])
    print(f"\n  {label}: similarity {s:+.3f}")
    print(f"    A: {a}")
    print(f"    B: {b}")

print()
print("=" * 70)
print("PART 4: an off-topic query still returns its top-k")
print("=" * 70)
off = "What is the best way to negotiate a mortgage rate?"
oscores = util.cos_sim(m.encode(off), cv)[0]
print(f"query: {off!r}\n")
for s, c in sorted(zip(oscores.tolist(), chunks), reverse=True)[:3]:
    print(f"  {s:+.3f}  {c}")
print("\n  nothing is relevant, but retrieval always returns something.")
print(f"  best off-topic {max(oscores.tolist()):+.3f} vs best on-topic "
      f"{max(scores.tolist()):+.3f} --- that narrow gap is the "
      f"relevance-threshold problem.")
