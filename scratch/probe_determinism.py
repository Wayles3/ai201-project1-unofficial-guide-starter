from answer import answer

q = "How many interview rounds does Meta have?"
for i in range(4):
    res = answer(q)
    print(f"run {i}: {res['answer'][:140]}")
