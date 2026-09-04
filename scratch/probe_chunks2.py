from query_index import search
for q in ["How do I prepare for a Google interview?", "How do I follow up after an interview?", "How long does the hiring process take?"]:
    print(f"\n=== {q} ===")
    for h in search(q, 5):
        print(f"  {h['score']:.3f} {h['meta']['source_file']:32} {' '.join(h['text'].split())[:100]}")
