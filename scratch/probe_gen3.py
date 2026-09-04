import re
from answer import answer

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
REFUSAL = re.compile(r"my sources don.t (cover|have)", re.I)
refused = 0
for q in QS:
    res = answer(q)
    is_ref = bool(REFUSAL.search(res["answer"]))
    refused += is_ref
    print(f"{'REFUSED ' if is_ref else 'answered'}  {q}")
    if is_ref:
        print(f"          {res['answer'][:160]}")
print(f"\n{refused}/{len(QS)} refused at generation")
