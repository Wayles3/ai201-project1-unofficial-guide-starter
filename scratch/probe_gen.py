from answer import answer

QS = [
    "What questions does Amazon ask in interviews?",
    "How do I prepare for a Google interview?",
    "What is the STAR method?",
    "How long does the hiring process take?",
    "How many interview rounds does Meta have?",
]
for q in QS:
    res = answer(q)
    refused = "don't cover" in res["answer"].lower() or "doesn't cover" in res["answer"].lower()
    print(f"\n{'REFUSED' if refused else 'answered'}  Q: {q}")
    print(f"  {res['answer'][:220]}")
