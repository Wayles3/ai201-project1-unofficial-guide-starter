"""Compare two embedding models on the on-topic / off-topic separation.

Backs the "a tested alternative that did not work" claim in planning.md.
Run: .venv/bin/python scratch/compare_models.py
"""

from sentence_transformers import SentenceTransformer, util

query = "how much practice is enough before applying?"
off_topic = "What is the best way to negotiate a mortgage rate?"
chunks = [
    "I solved 175 LeetCode problems: 52 easy, 106 medium, 17 hard.",
    "I studied for coding interview for an entire year.",
    "Most leetcode style questions are usually mediums.",
    "The average technical score across all users is 2.85 out of 4.",
    "Don't feel obligated to accept your offer right away; negotiation is a dialogue.",
]

for name in ["all-MiniLM-L6-v2", "multi-qa-MiniLM-L6-cos-v1"]:
    m = SentenceTransformer(name)
    cv = m.encode(chunks)
    print("=" * 68)
    print(name)
    print("=" * 68)
    on = util.cos_sim(m.encode(query), cv)[0].tolist()
    print(f"ON-TOPIC  {query!r}")
    for s, c in sorted(zip(on, chunks), reverse=True):
        print(f"   {s:+.3f}  {c[:60]}")
    off = util.cos_sim(m.encode(off_topic), cv)[0].tolist()
    print(f"OFF-TOPIC {off_topic!r}")
    print(f"   best score: {max(off):+.3f}")
    print(f"   >>> GAP (on-topic best minus off-topic best): {max(on) - max(off):+.3f}")
    neg = float(util.cos_sim(
        m.encode("Grinding LeetCode is absolutely worth your time."),
        m.encode("Grinding LeetCode is a waste of your time."))[0][0])
    print(f"   contradiction pair similarity: {neg:+.3f}")
    print()
