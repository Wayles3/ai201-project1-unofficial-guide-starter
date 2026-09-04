"""Milestone 1: collect raw source documents into documents/.

This is collection only — no chunking, no embedding. Each source is saved as a
plain .txt file with a small metadata header so that source URL, type, and fetch
date survive into the ingestion stage later.

Run:  .venv/bin/python collect_documents.py
"""

import csv
import html
import json
import re
import time
from collections import deque
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).parent / "documents"
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}
GH_RAW = "https://raw.githubusercontent.com"
TIH = f"{GH_RAW}/yangshun/tech-interview-handbook/main/apps/website/contents"

# type: guide | blog | thread | news | official
SOURCES = [
    # --- long sectioned guides (clean markdown, no HTML to strip) ---
    ("swe-interview-guide", "Tech Interview Handbook — SWE interview guide", "guide",
     f"{TIH}/software-engineering-interview-guide.md", "md"),
    ("behavioral-interview", "Tech Interview Handbook — behavioral interview", "guide",
     f"{TIH}/behavioral-interview.md", "md"),
    ("behavioral-questions", "Tech Interview Handbook — behavioral questions", "guide",
     f"{TIH}/behavioral-interview-questions.md", "md"),
    ("coding-study-plan", "Tech Interview Handbook — coding interview study plan", "guide",
     f"{TIH}/coding-interview-study-plan.md", "md"),
    ("coding-rubrics", "Tech Interview Handbook — coding interview rubrics", "guide",
     f"{TIH}/coding-interview-rubrics.md", "md"),
    ("behavioral-rubrics", "Tech Interview Handbook — behavioral interview rubrics", "guide",
     f"{TIH}/behavioral-interview-rubrics.md", "md"),
    ("negotiation", "Tech Interview Handbook — negotiation", "guide",
     f"{TIH}/negotiation.md", "md"),
    ("negotiation-rules", "Tech Interview Handbook — negotiation rules", "guide",
     f"{TIH}/negotiation-rules.md", "md"),
    ("resume", "Tech Interview Handbook — resume guide", "guide",
     f"{TIH}/resume.md", "md"),
    ("system-design-primer", "System Design Primer — main README", "guide",
     f"{GH_RAW}/donnemartin/system-design-primer/master/README.md", "md"),

    # --- data-driven blog posts ---
    ("iio-arbitrary", "interviewing.io — interview performance is kind of arbitrary", "blog",
     "https://interviewing.io/blog/after-a-lot-more-data-technical-interview-performance-really-is-kind-of-arbitrary", "html"),
    ("iio-600-interviews", "interviewing.io — 5 common problem areas from 600+ interviews", "blog",
     "https://interviewing.io/blog/ive-conducted-over-600-technical-interviews-on-interviewing-io-here-are-5-common-problem-areas-ive-seen", "html"),
    ("iio-practice-gap", "interviewing.io — the technical interview practice gap", "blog",
     "https://interviewing.io/blog/technical-interview-practice-gap", "html"),
    ("iio-language-style", "interviewing.io — language and code style analysis", "blog",
     "https://interviewing.io/blog/we-analyzed-thousands-of-technical-interviews-on-everything-from-language-to-code-style-here-s-what-we-found", "html"),
    ("levels-negotiation-guide", "Levels.fyi — Ultimate Negotiation Guide", "guide",
     "https://www.levels.fyi/blog/ultimate-negotiation-guide.html", "html"),
    ("marchenko-postmortem", "Andrei Marchenko — Cracking the FAANG interview (2024)", "blog",
     "https://amarchenko.dev/blog/2024-01-17-interview-experience/", "html"),

    # --- news / current-state ---
    ("computerworld-ai-cheating", "Computerworld — companies bring back in-person interviews", "news",
     "https://www.computerworld.com/article/4044734/to-counter-ai-cheating-companies-bring-back-in-person-job-interviews.html", "html"),

    # --- short forum threads (facts spread across replies) ---
    ("levels-newgrad-expedia", "Levels.fyi — New grad interview experience (Expedia, Blue Origin, eBay)", "thread",
     "https://www.levels.fyi/community/thread/1LBjuA/new-grad-interview-experience--expedia-group-blue-origin-ebay", "html"),
    ("levels-amazon-study", "Levels.fyi — How I studied for my Amazon SWE interview", "thread",
     "https://www.levels.fyi/community/thread/P2ow0q/how-i-studied-for-my-amazon-software-engineer-interview", "html"),
    ("levels-meta-rushed", "Levels.fyi — Interview with Meta, superficial and rushed?", "thread",
     "https://www.levels.fyi/community/thread/WZHFPx/interview-with-meta-superficial-and-rushed", "html"),
    ("levels-netflix-newgrad", "Levels.fyi — Interview process for new grad at Netflix (2022)", "thread",
     "https://www.levels.fyi/community/thread/qhpgkj/interview-process-for-new-grad-at-netflix", "html"),
    ("levels-paypal-newgrad", "Levels.fyi — PayPal SWE new grad interview", "thread",
     "https://www.levels.fyi/community/thread/cgmY4y/interview-paypal-software-engineer-new-grad", "html"),

    # --- large threaded discussions (via Algolia API) ---
    ("hn-ai-killed-interview", "Hacker News — AI killed the tech interview. Now what?", "thread",
     "https://news.ycombinator.com/item?id=43108673", "hn:43108673"),
    # NOTE: despite being an HN item, this is effectively a single long essay —
    # the thread drew only 2 comments, one of them ~9,700 chars. Kept as a
    # first-person critique of the hiring process, not as a discussion.
    ("hn-hiring-broken", "Hacker News — The Tech Hiring Process Is Broken (single long critique, 2 comments)", "thread",
     "https://news.ycombinator.com/item?id=39329929", "hn:39329929"),

    # --- official baseline, kept deliberately as a contrast source ---
    ("google-official-prep", "Google Careers — official SWE interview prep guide", "official",
     "https://www.google.com/about/careers/applications/candidate-prep/swe", "html"),
]

HN_MAX_CHARS = 60_000

# FIX 4: kept on disk as evidence, but not indexed — the page is client-rendered
# and yields only navigation labels, so indexing it would add pure noise.
EXCLUDE_FROM_INDEX = {"google-official-prep"}


# Block-level tags: each one ends a paragraph. Inserting a blank line after them
# is what preserves paragraph structure for the chunker downstream.
BLOCK_TAGS = ["p", "div", "li", "blockquote", "tr", "section", "article",
              "h1", "h2", "h3", "h4", "h5", "h6", "pre", "ul", "ol"]

# Exact boilerplate lines, matched case-insensitively after stripping.
JUNK_LINES = {
    # levels.fyi community chrome
    "about", "public", "members", "sort by:", "in", "tech", "reply", "share",
    "follow", "log in", "sign up",
    # interviewing.io site nav
    "interviewing.io", "for employers", "gift mock interviews", "blog", "faq",
    "questions", "& tips", "read 9 chapters for free", "→",
    # generic
    "main menu", "google apps", "home", "careers", "jobs", "students",
}


def clean_html(raw):
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "form", "noscript", "svg", "button"]):
        tag.decompose()
    # FIX 1: end every block element with a blank line so paragraphs survive.
    for tag in soup.find_all(BLOCK_TAGS):
        tag.append("\n\n")
    text = html.unescape(soup.get_text(" "))
    # normalise: collapse runs of spaces/tabs, trim each line, cap blank runs at one
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(ln.strip() for ln in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_markdown_cruft(text):
    """FIX 2: remove Docusaurus YAML frontmatter and leaked JSX from guides."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)       # frontmatter
    text = re.sub(r"<head>.*?</head>", "", text, flags=re.S | re.I)  # <head> block
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)               # HTML comments
    text = re.sub(r"^import\s+.*?;?\s*$", "", text, flags=re.M)      # MDX imports
    text = re.sub(r"</?[A-Za-z][^>]*/?>", "", text)                  # stray JSX/HTML tags
    # Leftover call-to-action buttons: the <a> wrapper is gone but its label
    # remains, e.g. "Book a free consultation with Rora &nbsp;→".
    text = re.sub(r"^(?:Book|Get|Try|Start|Sign up|Check out|Learn more)\b.*?"
                  r"(?:&nbsp;)?\s*(?:→|->)\s*$", "", text, flags=re.M | re.I)
    # Unescape AFTER tag stripping, so content placeholders written as
    # &lt;role&gt; survive as literal <role> instead of being deleted as tags.
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Site trailers: everything from here on is related-article links, newsletter
# prompts and category menus. Only cut if the marker appears late in the page,
# so a mid-article mention of the same words can't truncate real content.
TRAILER_MARKERS = [
    "SUBSCRIBE TO OUR", "Most Popular", "Related content", "Newsletter",
    "Sign up for our", "More from this author", "Show me more",
]

# Unambiguous site chrome: these phrases never appear in article prose, so they
# are cut wherever they appear rather than only late in the page. Needed because
# levels.fyi puts its "More from <category>" related-post block roughly halfway
# down a short thread, where the 0.55 guard below would not reach it.
HARD_TRAILER_PATTERNS = [
    r"^More from [A-Z][\w &/-]{0,30}$",
    r"^See all posts in\b",
    r"^More stories\b",
]


def drop_browser_title(text):
    """Remove the duplicated browser-title line, e.g.
    "New Grad Interview Experience (...) - Levels.fyi Community", which repeats
    the thread title a few lines later. Frees the opening-post budget for the
    poster's actual question.
    """
    lines = text.split("\n")
    for i, ln in enumerate(lines[:3]):
        if re.search(r" [-|–] (Levels\.fyi Community|Hacker News)\s*$", ln):
            del lines[i]
            break
    return "\n".join(lines)


def cut_site_trailer(text, min_fraction=0.55):
    cut = len(text)
    for marker in TRAILER_MARKERS:
        i = text.find(marker)
        if i > len(text) * min_fraction:
            cut = min(cut, i)
    for pattern in HARD_TRAILER_PATTERNS:
        m = re.search(pattern, text, flags=re.M)
        # still require *some* content first, so a malformed page can't empty out
        if m and m.start() > 200:
            cut = min(cut, m.start())
    return text[:cut].strip()


def drop_boilerplate(text, dtype):
    """FIX 3: drop known junk lines, and bare vote/view counts inside threads."""
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        low = s.lower()
        if low in JUNK_LINES:
            continue
        # in forum threads, lines that are only a number are vote/view counters
        if dtype == "thread" and re.fullmatch(r"[\d,]{1,9}", s):
            continue
        # lone emoji / single punctuation artifacts
        if s and len(s) <= 2 and not s.isalnum():
            continue
        out.append(ln)
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def flatten_hn(root, max_chars=None):
    """Breadth-first flatten of an Algolia HN item tree into readable text.

    Breadth-first on purpose: when the character budget runs out we want to have
    spent it on many distinct top-level opinions rather than on a few argument
    threads followed to full depth. Retrieval benefits more from diverse chunks
    than from any one thread being complete.
    """
    def count_all(n):
        c = 1 if (n.get("text") or n.get("title")) else 0
        return c + sum(count_all(ch) for ch in n.get("children", []))

    available = count_all(root)
    acc, total, kept = [], 0, 0
    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        txt = node.get("text") or node.get("title") or ""
        if txt:
            txt = clean_html(txt)
            author = node.get("author") or "anon"
            entry = f"{'  ' * min(depth, 6)}[{author}] {txt}"
            if max_chars is not None and total + len(entry) > max_chars:
                acc.append(
                    f"[TRUNCATED at {max_chars} chars: captured {kept} of "
                    f"{available} comments, breadth-first]")
                break
            acc.append(entry)
            total += len(entry)
            kept += 1
        for child in node.get("children", []):
            queue.append((child, depth + 1))
    return acc


def fetch(url, kind, dtype):
    if kind.startswith("hn:"):
        item_id = kind.split(":", 1)[1]
        r = requests.get(f"https://hn.algolia.com/api/v1/items/{item_id}",
                         headers=UA, timeout=40)
        r.raise_for_status()
        return "\n\n".join(flatten_hn(json.loads(r.text), HN_MAX_CHARS))
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    if kind == "md":
        return strip_markdown_cruft(r.text)
    return cut_site_trailer(drop_browser_title(
        drop_boilerplate(clean_html(r.text), dtype)))


def main():
    OUT.mkdir(exist_ok=True)
    today = date.today().isoformat()
    rows = []
    for i, (slug, title, dtype, url, kind) in enumerate(SOURCES, start=1):
        name = f"{i:02d}-{slug}.txt"
        try:
            text = fetch(url, kind, dtype)
        except Exception as exc:
            print(f"  !! {name}  FAILED  {type(exc).__name__}: {exc}")
            rows.append([i, slug, title, dtype, url, "FAILED", 0, 0, 0, False])
            continue
        indexed = slug not in EXCLUDE_FROM_INDEX
        header = (
            f"---\n"
            f"id: {i:02d}\n"
            f"title: {title}\n"
            f"type: {dtype}\n"
            f"url: {url}\n"
            f"fetched: {today}\n"
            f"index: {str(indexed).lower()}\n"
            f"---\n\n"
        )
        (OUT / name).write_text(header + text + "\n", encoding="utf-8")
        words = len(text.split())
        paras = len([p for p in text.split("\n\n") if p.strip()])
        flag = "" if indexed else "  [EXCLUDED from index]"
        print(f"  ok {name:44} {len(text):>7} chars  {paras:>5} paras{flag}")
        rows.append([i, slug, title, dtype, url, "ok", len(text), words, paras, indexed])
        time.sleep(0.7)

    with (OUT / "_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "slug", "title", "type", "url", "status",
                    "chars", "words", "paragraphs", "index"])
        w.writerows(rows)
    ok = sum(1 for r in rows if r[5] == "ok")
    idx = sum(1 for r in rows if r[5] == "ok" and r[9])
    print(f"\n{ok}/{len(rows)} sources saved to documents/  ({idx} will be indexed)")


if __name__ == "__main__":
    main()
