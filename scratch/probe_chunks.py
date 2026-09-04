from query_index import search
for q in ["How do I explain a gap in my resume?", "What should I wear to an interview?"]:
    print(f"\n=== {q} ===")
    for h in search(q, 5):
        print(f"  {h['score']:.3f} {h['meta']['source_file']:32} {' '.join(h['text'].split())[:90]}")
