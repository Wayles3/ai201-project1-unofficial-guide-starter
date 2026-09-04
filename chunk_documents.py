"""Milestone 2: split documents/ into retrievable chunks.

Run:  .venv/bin/python chunk_documents.py

The plumbing is written for you. Three things are yours to decide and implement
--- they are marked TODO(you). Everything else you can read but need not change.
"""

import json
import re
from pathlib import Path

DOCS = Path(__file__).parent / "documents"
OUT = Path(__file__).parent / "chunks.json"


# ---------------------------------------------------------------------------
# TODO(you) #1 --- pick your numbers.
#
# Guidance, not answers:
#   * all-MiniLM-L6-v2 truncates input at 256 word-pieces, very roughly
#     ~1000 characters of English. Chunks bigger than that get silently
#     cut off during embedding --- the tail is invisible to retrieval.
#   * Smaller chunks = sharper matches but more risk of failing the
#     standalone test. Larger chunks = safer context but blunter matches.
#   * MIN_CHARS drops fragments too small to be useful on their own
#     (a stray heading, a one-word line).
# Start with a guess, run the script, look at the output, then adjust.
# ---------------------------------------------------------------------------
TARGET_CHARS = 800      # e.g. 400? 800? 1000?
OVERLAP_CHARS = 300    # e.g. 0? 100? 200?
MIN_CHARS = 100         # e.g. 50? 100?


def load_documents():
    """Read documents/*.txt, parse the metadata header, skip index: false."""
    docs = []
    for path in sorted(DOCS.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            continue
        header, body = raw.split("---\n\n", 1)
        meta = {}
        for line in header.splitlines():
            if ": " in line:
                key, val = line.split(": ", 1)
                meta[key.strip()] = val.strip()
        if meta.get("index") == "false":
            continue
        meta["body"] = body.strip()
        meta["file"] = path.name
        docs.append(meta)
    return docs


def split_markdown_sections(body):
    """Split Markdown at headings, returning (heading_path, text) pairs.

    Tracks the heading stack so nested headings produce a breadcrumb like
    "Negotiation services > Rora". This is what stops a chunk from talking
    about "Rora" without ever saying what Rora is.
    """
    sections, stack, cur, path = [], {}, [], ""
    for line in body.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if cur:
                sections.append((path, "\n".join(cur).strip()))
            level, title = len(m.group(1)), m.group(2).strip()
            stack[level] = title
            for lvl in [l for l in stack if l > level]:
                del stack[lvl]
            path = " > ".join(stack[l] for l in sorted(stack))
            cur = []
        else:
            cur.append(line)
    if cur:
        sections.append((path, "\n".join(cur).strip()))
    return [(p, t) for p, t in sections if t]


def paragraphs_of(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]


# ---------------------------------------------------------------------------
# TODO(you) #4 --- tune the non-prose filter, then verify what it deleted.
#
# These two thresholds decide what counts as "navigation, not writing".
# Raise them to delete less, lower them to delete more.
#   MAX_LINK_PAYLOAD_RATIO: fraction of a chunk's characters that are link
#                           machinery (URLs, markdown link targets, table and
#                           bullet syntax) rather than words.
#
# NOTE: an earlier version of this filter dropped any chunk that was mostly
# markdown TABLE rows. That was wrong --- it deleted the coding-rubrics table,
# the study-plan priority table and the resume section table, which are the
# highest-information content in the corpus. Tables here are data, not
# navigation. What we actually want to drop is text whose payload is URLs.
#
# Measured separation on this corpus:
#     content tables and prose   ratio 0.05 - 0.74
#     link tables and TOC        ratio 0.81 - 0.99
# The margin is narrow (0.74 vs 0.81), so this threshold is fragile --- if you
# add sources, re-measure rather than trusting it.
# After running, read what got dropped (the script prints samples) and check
# that no real prose was caught. That check is the actual assignment here.
# ---------------------------------------------------------------------------
MAX_LINK_PAYLOAD_RATIO = 0.78

# How much of a forum thread counts as "the opening post" --- the question that
# gets prepended to every chunk from that thread (policy (b), TODO #3).
OPENING_POST_CHARS = 420

DROPPED = {"too_small": 0, "non_prose": 0}
DROPPED_SAMPLES = []


def link_payload_ratio(text):
    """Fraction of characters that are link machinery rather than words.

    Keeps the visible text of a markdown link and throws away its target, then
    strips bare URLs and table/bullet punctuation. What remains is the words a
    reader would actually read. A high ratio means the chunk is navigation.
    """
    stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text
    stripped = re.sub(r"https?://\S+", "", stripped)          # bare URLs
    stripped = re.sub(r"[|\-\s*]+", " ", stripped)            # table/bullet syntax
    return 1 - (len(stripped.strip()) / max(len(text), 1))


def looks_like_prose(text):
    """False for link tables and tables of contents. Content tables pass."""
    return link_payload_ratio(text) <= MAX_LINK_PAYLOAD_RATIO


def split_long_paragraph(para, target):
    """Fallback ladder: sentences, then hard character cuts as a last resort.

    This is the same greedy loop as pack_paragraphs, one level down: accumulate
    sentences until the next one won't fit, then flush.
    """
    sentences = re.split(r"(?<=[.!?])\s+", para)
    out, cur, size = [], [], 0
    for sent in sentences:
        # a single sentence longer than target can't be packed --- cut it
        if len(sent) > target:
            if cur:
                out.append(" ".join(cur))
                cur, size = [], 0
            for i in range(0, len(sent), target):
                out.append(sent[i:i + target])
            continue
        if size + len(sent) > target and cur:
            out.append(" ".join(cur))
            cur, size = [], 0
        cur.append(sent)
        size += len(sent)
    if cur:
        out.append(" ".join(cur))
    return out


# ---------------------------------------------------------------------------
# TODO(you) #2 --- the core function.
#
# Take a list of paragraphs, return a list of chunk strings.
#
# Start from pack_paragraphs_no_overlap() in the lesson: greedily add
# paragraphs until the next one would exceed `target`, then emit.
#
# Then add overlap. When you emit a chunk and start the next one, seed the
# new chunk with the TAIL of what you just emitted --- roughly `overlap`
# characters' worth --- so a fact sitting on the boundary lands in both.
#
# Things to think about (no single right answer):
#   * If one paragraph is on its own longer than `target`, what should
#     happen? Emitting it oversized means the embedder truncates it.
#       Splitting it means cutting mid-paragraph. Pick one and be able to
#       say why.
#   * Should overlap be whole paragraphs, or a raw character slice?
#     Whole paragraphs keep chunks readable; character slices give you
#     precise control over size.
# ---------------------------------------------------------------------------
def pack_paragraphs(paragraphs, target, overlap):
    chunks = []
    current = []
    size = 0

    # STAGE 4: any paragraph bigger than target is replaced by its
    # sentence-packed pieces before the loop below ever sees it. This is what
    # stops `target` from being a mere flush threshold --- now nothing longer
    # than target enters the loop, so nothing can overshoot by a whole
    # paragraph. The loop itself is unchanged.
    units = []
    for para in paragraphs:
        if len(para) > target:
            units.extend(split_long_paragraph(para, target))
        else:
            units.append(para)

    for para in units:
        if size + len(para) > target and current:
            chunks.append("\n\n".join(current))
            # seed the next chunk with trailing paragraphs, up to `overlap` chars
            carry, carry_size = [], 0
            for p in reversed(current):
                if carry_size + len(p) > overlap:
                    break
                carry.insert(0, p)
                carry_size += len(p)
            current = carry
            size = carry_size
        current.append(para)
        size += len(para)

    if current:
        chunks.append("\n\n".join(current))
    return chunks




def chunk_document(doc):
    """Dispatch on document type, then attach metadata to every chunk."""
    dtype = doc.get("type", "blog")
    pieces = []   # list of (heading_path, text)

    if dtype == "guide" and "#" in doc["body"]:
        for path, text in split_markdown_sections(doc["body"]):
            paras = paragraphs_of(text)
            if not paras:
                continue
            for piece in pack_paragraphs(paras, TARGET_CHARS, OVERLAP_CHARS):
                pieces.append((path, piece))

    elif dtype == "thread":
        # ------------------------------------------------------------------
        # TODO(you) #3 --- decide the thread policy.
        #
        # You found that 18-levels-newgrad-expedia.txt only makes sense as a
        # whole: the question is in the first paragraph and the answers are
        # spread across replies. Splitting it destroys the answer.
        #
        # But 23-hn-ai-killed-interview.txt is 60,000 characters. Keeping
        # THAT whole is impossible --- it would be one giant chunk that the
        # embedder truncates to its first ~1000 characters.
        #
        # So: what's your rule? Some options ---
        #   (a) keep the thread whole if under some size, else pack it
        #   (b) always keep the opening post, and attach it to every chunk
        #       (like a breadcrumb) so replies never lose their question
        #   (c) one chunk per comment, with the opening post prepended
        # Implement one. Option (b) is the most interesting and reuses the
        # breadcrumb idea you already understand.
        # ------------------------------------------------------------------
        # POLICY (b): the opening post is prepended to every chunk from the
        # thread, so a reply can never be retrieved without the question it
        # answers. This is the breadcrumb idea applied to conversation instead
        # of headings, and it directly addresses the Expedia trap: a chunk of
        # generic replies always carries the question naming Expedia, Blue
        # Origin and eBay alongside it, so the model can see that the replies
        # do not actually mention those companies.
        paras = paragraphs_of(doc["body"])
        # Take opening paragraphs while they FIT the budget --- checking after
        # the fact would let a single huge paragraph in whole (which is exactly
        # the overshoot bug that made TARGET_CHARS a mere flush threshold).
        opening, taken = [], 0
        for para in paras:
            if opening and taken + len(para) > OPENING_POST_CHARS:
                break
            opening.append(para)
            taken += len(para)
        header = "\n\n".join(opening)
        if len(header) > OPENING_POST_CHARS:
            # the very first paragraph alone busts the budget: use a truncated
            # preview as the header, and leave the full text in the body
            header = header[:OPENING_POST_CHARS].rsplit(" ", 1)[0] + " ..."
            rest = paras
        else:
            rest = paras[len(opening):]

        if not rest:
            pieces.append(("", header))
        else:
            # leave room for the header in every chunk, but never go below a
            # workable floor for the reply text itself
            budget = max(TARGET_CHARS - len(header) - 8, 200)
            # Overlap must scale with the budget it operates in. At the full
            # OVERLAP_CHARS, carried text plus a new paragraph can approach
            # 2x the reply budget, and adding the header on top pushed chunks
            # past the embedder limit. Threads also need paragraph overlap
            # least, because the opening post is already repeated in every
            # chunk --- that repetition is doing the same job.
            thread_overlap = min(OVERLAP_CHARS, budget // 3)
            for piece in pack_paragraphs(rest, budget, thread_overlap):
                pieces.append(("", f"{header}\n\n--- replies ---\n\n{piece}"))

    else:  # blog, news --- paragraphs only, no headings to key on
        for piece in pack_paragraphs(paragraphs_of(doc["body"]),
                                     TARGET_CHARS, OVERLAP_CHARS):
            pieces.append(("", piece))

    chunks = []
    for i, (path, text) in enumerate(pieces):
        if MIN_CHARS is not None and len(text) < MIN_CHARS:
            DROPPED["too_small"] += 1
            continue
        if not looks_like_prose(text):
            DROPPED["non_prose"] += 1
            if len(DROPPED_SAMPLES) < 8:
                DROPPED_SAMPLES.append((doc.get("file", ""), text))
            continue
        breadcrumb = " > ".join(x for x in [doc.get("title", ""), path] if x)
        chunks.append({
            "text": text,
            "heading_path": breadcrumb,
            "source_id": doc.get("id", "??"),
            "source_title": doc.get("title", ""),
            "source_url": doc.get("url", ""),
            "source_type": doc.get("type", ""),
            "source_file": doc.get("file", ""),
            "chunk_index": i,
        })
    return chunks


def report(chunks):
    """Print the diagnostics you need to judge whether your numbers are sane."""
    if not chunks:
        print("no chunks produced")
        return
    sizes = sorted(len(c["text"]) for c in chunks)
    n = len(sizes)
    print(f"\n{n} chunks from {len({c['source_id'] for c in chunks})} documents")
    print(f"  min {sizes[0]}   median {sizes[n // 2]}   max {sizes[-1]}")
    print(f"  mean {sum(sizes) // n}   total {sum(sizes):,} chars")
    over = [s for s in sizes if s > 1000]
    if over:
        print(f"  !! {len(over)} chunks over 1000 chars "
              f"(embedder will truncate these)")
    by_type = {}
    for c in chunks:
        by_type.setdefault(c["source_type"], []).append(len(c["text"]))
    print("\n  by source type:")
    for k, v in sorted(by_type.items()):
        print(f"    {k:9} {len(v):>4} chunks   mean {sum(v) // len(v):>5} chars")
    print(f"\n  dropped: {DROPPED['too_small']} too small (<{MIN_CHARS}), "
          f"{DROPPED['non_prose']} judged non-prose")
    if DROPPED_SAMPLES:
        print("\n  VERIFY THESE --- did the filter eat any real writing?")
        for fname, text in DROPPED_SAMPLES:
            first = " ".join(text.split())[:110]
            print(f"    {fname[:28]:28} | {first}")

    print("\n  three sample chunks:")
    for c in [chunks[0], chunks[n // 2], chunks[-1]]:
        print(f"\n    [{c['heading_path'][:70]}]")
        print(f"    {c['text'][:200]!r}...")


def main():
    missing = [name for name, val in
               [("TARGET_CHARS", TARGET_CHARS), ("OVERLAP_CHARS", OVERLAP_CHARS),
                ("MIN_CHARS", MIN_CHARS)] if val is None]
    if missing:
        print(f"Set these first (TODO #1): {', '.join(missing)}")
        return

    docs = load_documents()
    print(f"loaded {len(docs)} documents")
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    report(all_chunks)
    OUT.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
