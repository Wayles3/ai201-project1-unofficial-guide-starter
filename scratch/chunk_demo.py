"""Show what three different chunking strategies do to ONE real paragraph."""

text = """**Here's something that recruiters don't want you to know -** In most cases, there's room for negotiation on your offer and recruiters expect candidates to negotiate. **The initial offer that you are given is never the best package that the company can offer.** During my last job hunting experience, I received offers from numerous top tech companies like Facebook, Google, Airbnb, Lyft, Dropbox, and I have found this to be true."""

print("=" * 72)
print("STRATEGY A: fixed 150 characters, no overlap")
print("=" * 72)
for i in range(0, len(text), 150):
    piece = text[i:i + 150]
    print(f"\n  CHUNK {i//150 + 1}:")
    print(f"  |{piece}|")

print()
print("=" * 72)
print("STRATEGY B: fixed 150 characters, 50-character overlap")
print("=" * 72)
step = 150 - 50
n = 1
for i in range(0, len(text), step):
    piece = text[i:i + 150]
    if not piece.strip():
        break
    print(f"\n  CHUNK {n}:")
    print(f"  |{piece}|")
    n += 1

print()
print("=" * 72)
print("STRATEGY C: split on sentence boundaries")
print("=" * 72)
import re
sentences = re.split(r"(?<=\.) ", text)
for n, s in enumerate(sentences, 1):
    print(f"\n  CHUNK {n}:")
    print(f"  |{s}|")
