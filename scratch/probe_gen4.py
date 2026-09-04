import re
from answer import answer

IN_DOMAIN = [
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
MUST_REFUSE = [
    "What is the best way to negotiate a mortgage rate?",
    "What are good interview questions for a nursing job?",
    "What is the capital of Australia?",
]
REFUSAL = re.compile(r"my sources don.t (cover|have)", re.I)

print("### IN-DOMAIN (should mostly ANSWER now) ###")
refused = 0
for q in IN_DOMAIN:
    res = answer(q)
    is_ref = bool(REFUSAL.search(res["answer"]))
    refused += is_ref
    print(f"{'REFUSED ' if is_ref else 'answered'}  {q}")
    if is_ref:
        print(f"          {res['answer'][:150]}")
print(f"\n{refused}/{len(IN_DOMAIN)} refused (was 6/15 before the fix)")

print("\n### MUST-REFUSE CONTROLS (should still refuse) ###")
still_ok = 0
for q in MUST_REFUSE:
    res = answer(q)
    is_ref = bool(REFUSAL.search(res["answer"])) or res["refused_at"] is not None
    still_ok += is_ref
    print(f"{'REFUSED ' if is_ref else 'LEAKED! '}  {q}")
    print(f"          {res['answer'][:150]}")
print(f"\n{still_ok}/{len(MUST_REFUSE)} correctly still refused")
