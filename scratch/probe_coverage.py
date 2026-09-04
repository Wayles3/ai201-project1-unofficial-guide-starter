from query_index import search, RELEVANCE_FLOOR

QS = [
    "What questions does Amazon ask in interviews?",
    "How do I prepare for a Google interview?",
    "What is the STAR method?",
    "How long does the hiring process take?",
    "What should I wear to an interview?",
    "How do I answer 'tell me about yourself'?",
    "What is a take-home assignment?",
    "How do I negotiate my salary?",
    "What is a system design interview?",
    "How many interview rounds does Meta have?",
    "What is behavioral interviewing?",
    "Should I use Python or Java in interviews?",
    "How do I explain a gap in my resume?",
    "What is the STAR format for answers?",
    "How do I follow up after an interview?",
]
for q in QS:
    hits = search(q, 5)
    best = max(h["score"] for h in hits)
    status = "REFUSED" if best < RELEVANCE_FLOOR else "answered"
    print(f"{status:8} best={best:.3f}  {q}")
