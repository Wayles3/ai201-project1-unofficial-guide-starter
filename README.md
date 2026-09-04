# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

New-grad software engineering interview preparation: what the hiring process at large tech
companies actually looks like from the candidate's side — how many rounds there are, what LeetCode
difficulty to expect, whether interviewers give hints, how much preparation is realistic, and
whether the first offer a company makes is negotiable.

This is valuable and hard to find officially for a specific reason: official careers pages publish
process-level advice ("explain your thought process") but not outcome-level detail — realistic
timelines, question difficulty, whether a given number is normal. Google's own SWE prep page
([documents/25-google-official-prep.txt](documents/25-google-official-prep.txt)) is client-rendered
and yields **200 characters of navigation labels** when fetched as text; it contains no retrievable
guidance at all. The operational detail candidates actually need — "was 175 LeetCode problems
enough," "do Expedia interviewers give hints" — exists only in scattered first-hand accounts: forum
threads, personal blog postmortems, and interviewer-side data posts. It is also unusually
perishable: the 2026 hiring market has shifted toward in-person interviews in response to
AI-assisted cheating (measured at 72.4% of recruiting leaders, per a Gartner survey reported by
Computerworld), so advice even two years old can be confidently wrong, and no official source flags
which parts have expired.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

All 25 sources are collected by `collect_documents.py`; 24 are indexed (source 25 is kept as a
deliberate contrast example — see Domain above — but excluded because it has no extractable text).

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Tech Interview Handbook — SWE interview guide | guide | `documents/01-swe-interview-guide.txt` |
| 2 | Tech Interview Handbook — behavioral interview | guide | `documents/02-behavioral-interview.txt` |
| 3 | Tech Interview Handbook — behavioral questions | guide | `documents/03-behavioral-questions.txt` |
| 4 | Tech Interview Handbook — coding study plan | guide | `documents/04-coding-study-plan.txt` |
| 5 | Tech Interview Handbook — coding rubrics | guide | `documents/05-coding-rubrics.txt` |
| 6 | Tech Interview Handbook — behavioral rubrics | guide | `documents/06-behavioral-rubrics.txt` |
| 7 | Tech Interview Handbook — negotiation | guide | `documents/07-negotiation.txt` |
| 8 | Tech Interview Handbook — negotiation rules | guide | `documents/08-negotiation-rules.txt` |
| 9 | Tech Interview Handbook — resume guide | guide | `documents/09-resume.txt` |
| 10 | System Design Primer (GitHub README) | guide | `documents/10-system-design-primer.txt` |
| 11 | interviewing.io — interview performance is kind of arbitrary | blog | `documents/11-iio-arbitrary.txt` |
| 12 | interviewing.io — 5 problem areas from 600+ interviews | blog | `documents/12-iio-600-interviews.txt` |
| 13 | interviewing.io — the technical interview practice gap | blog | `documents/13-iio-practice-gap.txt` |
| 14 | interviewing.io — language and code style analysis | blog | `documents/14-iio-language-style.txt` |
| 15 | Levels.fyi — Ultimate Negotiation Guide | guide | `documents/15-levels-negotiation-guide.txt` |
| 16 | Andrei Marchenko — Cracking the FAANG interview (2024) | blog | `documents/16-marchenko-postmortem.txt` |
| 17 | Computerworld — companies bring back in-person interviews | news | `documents/17-computerworld-ai-cheating.txt` |
| 18 | Levels.fyi Community — new grad, Expedia/Blue Origin/eBay | thread | `documents/18-levels-newgrad-expedia.txt` |
| 19 | Levels.fyi Community — how I studied for Amazon SWE | thread | `documents/19-levels-amazon-study.txt` |
| 20 | Levels.fyi Community — Meta interview, superficial and rushed | thread | `documents/20-levels-meta-rushed.txt` |
| 21 | Levels.fyi Community — Netflix new grad process (2022) | thread | `documents/21-levels-netflix-newgrad.txt` |
| 22 | Levels.fyi Community — PayPal new grad interview | thread | `documents/22-levels-paypal-newgrad.txt` |
| 23 | Hacker News — "AI killed the tech interview. Now what?" (628 comments, sampled breadth-first) | thread | `documents/23-hn-ai-killed-interview.txt` |
| 24 | Hacker News — "The Tech Hiring Process Is Broken" (single long critique) | thread | `documents/24-hn-hiring-broken.txt` |
| 25 | Google Careers — official SWE prep guide (excluded from index; kept as evidence) | official | `documents/25-google-official-prep.txt` |

Variety across the corpus: guides cover structured advice (behavioral, resume, negotiation, system
design); blogs and the news article carry data-driven or narrative claims with specific numbers;
threads carry short, contradictory, first-hand opinions, including one thread with zero replies
(source 21) and one thread whose replies never address the companies it names (source 18) — both
kept deliberately, see Anticipated Challenges in `planning.md`.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 800 characters (target), enforced by a fallback ladder so nothing exceeds it by more
than one trailing sentence.

**Overlap:** 300 characters, carried as **whole paragraphs** rather than a character slice. Scaled
down automatically inside forum threads (to one third of the available reply budget) because the
opening post is already repeated in every chunk of a thread and is doing the same job.

**Minimum chunk size:** 100 characters.

**Preprocessing before chunking:** `collect_documents.py` fetches each source and strips, in order —
`<script>/<style>/<nav>/<footer>/<header>/<aside>/<form>/<button>` elements; Docusaurus YAML
frontmatter, `<head>` blocks, HTML comments and MDX `import` statements from the Markdown guides;
leftover call-to-action button labels (e.g. `"Book a free consultation with Rora &nbsp;→"`); site
trailers (newsletter prompts, "More from &lt;category&gt;" related-post blocks, "See all posts in");
forum chrome (vote counts, view counts, "Sort by:", member counts, duplicated browser-title lines);
and finally HTML entities are unescaped *after* tag stripping, so content placeholders written as
`&lt;role&gt;` survive as literal `<role>` instead of being deleted as tags. Blank lines are
deliberately preserved so paragraph boundaries exist for the chunker to split on.

**Why these choices fit your documents:**

The corpus spans **200x in document size** (462 characters to 105,000) across three structural
shapes, so each number was set against a measurement rather than a convention.

*Why 800 and not 400.* The ceiling is the embedding model: `all-MiniLM-L6-v2` truncates at ~256
word-pieces (~1,000 characters) and silently ignores the rest. The floor came from measuring the
corpus — **the median paragraph is 266 characters**. An initial target of 400 turned out to be
completely inert: two typical paragraphs exceed it, so the packer emitted one paragraph per chunk and
merged nothing. Verified directly — **0 of 879 chunks contained more than one paragraph.** Raising
the target to 800 (3× the median paragraph) made packing work and recovered 25,585 characters that
the minimum-size filter had been discarding.

*Why 300 overlap.* Because the carry is measured in whole paragraphs, the overlap budget must exceed
the typical paragraph or nothing can be carried. At 200 against a 266 median, overlap fired on only
**29% of chunk boundaries**. At 300 it clears the median. Whole paragraphs rather than character
slices, because slicing mid-sentence produces chunks that open like `es to negotiate.` — broken to
both a reader and the model. Cost: ~9% duplicated text, accepted deliberately.

*Why a fallback ladder was needed.* `TARGET_CHARS` is a *flush threshold*, not a cap — the packing
loop decides whether to emit before appending the next paragraph, but never rejects or splits the
incoming one. The real ceiling was therefore `overlap + largest paragraph`, and **12% of chunks
exceeded the target, the worst by 6.5×** (5,221 characters, of which the embedder would read the
first ~1,000). The ladder tries paragraphs, then sentences if a paragraph is over target, then a hard
character cut if a single sentence is. Max chunk size fell from 5,221 to **1,079**, and chunks over
1,000 fell from 34 to **3**.

*Why chunking is per document type.* Markdown guides are split at headings first, with the heading
path stored as a breadcrumb (`Negotiation > Negotiation services > Rora`) — added after finding a
chunk that discussed "Rora" without ever saying Rora is a negotiation service. Blogs and news have
no surviving headings, so they are packed by paragraph. Forum threads get the opening post prepended
to every chunk, so a reply is never retrievable without the question it answers.

**Final chunk count:** **868 chunks** from 24 indexed documents — median 620, mean 599, max 1,079,
520,230 characters total. Within the 50–2,000 sanity range. By source type: 451 guide, 237 thread,
159 blog, 21 news. Dropped during chunking: 23 fragments under 100 characters, and 9 chunks judged
non-prose (all `system-design-primer` link tables, a table of contents and a language switcher).

---

## Sample Chunks

<!-- Paste 5 representative chunks from your document collection after running your ingestion pipeline.
     For each chunk, note which source document it came from.
     These must be actual text — not screenshots. -->

Five chunks produced by `chunk_documents.py`, one per document type, each chosen because it contains
a fact that one of the five evaluation questions asks for. Full text of each is below the table.

| # | Source document | Type | Chars | Chunk text (opening) |
|---|----------------|------|-------|----------------------|
| 1 | `05-coding-rubrics.txt` | guide | 485 | "There are 2 general methods of candidate scoring in coding interviews…" |
| 2 | `18-levels-newgrad-expedia.txt` | thread | 811 | "New Grad Interview Experience (Expedia Group, Blue Origin, eBay)… How difficult were the leetcode questions, did the interviewers give hints, etc?" |
| 3 | `16-marchenko-postmortem.txt` | blog | 548 | "As an example, I have solved a total of 175 LeetCode tasks (52 easy, 106 medium, 17 hard)…" |
| 4 | `17-computerworld-ai-cheating.txt` | news | 421 | "According to a recent Gartner survey, 72.4% of recruiting leaders reported they are currently conducting interviews in-person to combat fraud…" |
| 5 | `13-iio-practice-gap.txt` | blog | 683 | "In a previous post, we talked about how women quit interview practice 7 times more often than men after just one bad interview…" |

---

### Chunk 1 — `05-coding-rubrics.txt` (guide, 485 chars)

**Breadcrumb:** `Tech Interview Handbook — coding interview rubrics > Candidate scoring methodology`

```
There are 2 general methods of candidate scoring in coding interviews:

1. Provide a score (e.g. 1-4) for every dimension and sum them up into an overall score
1. Provide an overall score (e.g. 1-4) based on overall performance across dimensions

Regardless of the method used, the scoring bands are generally:

- Strong hire
- Hire
- No hire
- Strong no hire

Some companies may have a middle band for indecision when the interviewer feels that the candidate requires more assessment.
```

**Standalone test: passes.** Names both scoring methods and lists all four bands without depending on
surrounding text. This chunk is also evidence for the chunking decision described above — an earlier
version of the non-prose filter deleted the rubrics table because it was mostly markdown table rows.

---

### Chunk 2 — `18-levels-newgrad-expedia.txt` (thread, 811 chars)

**Breadcrumb:** `Levels.fyi — New grad interview experience (Expedia, Blue Origin, eBay)`

```
kyle04   in   🖥️   Tech

Software Engineer

New Grad Interview Experience (Expedia Group, Blue Origin, eBay)

I've recently heard back from the companies listed above for entry-level software engineer positions.

I was wondering what the interview experience was like for these companies. How difficult were the leetcode questions, did the interviewers give hints, etc?

Thanks!

ramenenjoyer Software Engineer   at  ...

--- replies ---

yeef Software Engineer   at  The University of Texas at El Paso

Im also applying and interviewing with companies for entry level positions, and have noticed most leetcode style questions are usually mediums. As long as you are explaining your thought process and decision making to the interviewer, they will usually guide you in the right direction, or maybe even a hint
```

**Standalone test: passes, and does specific work.** Everything above `--- replies ---` is the
opening post, prepended to every chunk from this thread by design. It matters here because the
thread asks about **Expedia, Blue Origin and eBay** and *none of the six replies mentions any of
them*. Keeping the question attached means a model reading this chunk can see that the reply gives
general market advice, not company-specific experience — instead of silently attributing "usually
mediums" to Expedia. This is the attribution-hallucination risk recorded in `planning.md`.

**Known blemish:** the line `ramenenjoyer Software Engineer at ...` is a dangling author attribution
whose comment body sits in the previous chunk — an artifact of paragraph-level overlap landing on an
author line. Cosmetic, but it is real and left visible rather than hidden.

---

### Chunk 3 — `16-marchenko-postmortem.txt` (blog, 548 chars)

**Breadcrumb:** `Andrei Marchenko — Cracking the FAANG interview (2024)`

```
My preparation for Coding interviews

As an example, I have solved a total of 175 LeetCode tasks (52 easy, 106 medium, 17 hard) (some tasks I have already solved 3+ times). I also have an additional repository where I solve tasks that don't have Leetcode or are under premium with 80 solved tasks. Additionally, I passed courses related to algorithmics and watched a lot of videos about algorithms. As a recommendation, prepare by a list of important tasks like blind 75 and similar lists based on algorithmic approaches .

System design interviews

```

**Standalone test: passes.** Carries the full count *and* its difficulty breakdown in one sentence,
which is exactly the failure mode chunking is meant to avoid — an earlier configuration split
"175 LeetCode tasks" from "(52 easy, 106 medium, 17 hard)".

**Known blemish:** the trailing line `System design interviews` is the *next* section's heading. HTML
sources lose their heading markup during conversion, so section titles survive only as ordinary
paragraphs and can be absorbed at the end of a chunk, where they look like content. Affects blog and
news chunks only; the Markdown guides split on real headings and do not have this problem.

---

### Chunk 4 — `17-computerworld-ai-cheating.txt` (news, 421 chars)

**Breadcrumb:** `Computerworld — companies bring back in-person interviews`

```
To battle that trend, more and more companies are ditching screens for handshakes — bringing back in-person job interviews.

According to a recent Gartner survey , 72.4% of recruiting leaders reported they are currently conducting interviews in-person to combat fraud. Gartner defines candidate fraud as a would-be hire that pretends to be someone else and/or has someone else complete an interview pretending to be them.
```

**Standalone test: passes, and is worth contrasting with an earlier failure.** The statistic arrives
with its source named (Gartner) *and* a definition of the term it measures. Before packing was
working, this same document produced a chunk reading `"…I think that perspective will fade quickly,"
he said` — a quotation with no attribution at all, because the speaker's name was in the preceding
paragraph. Packing paragraphs together is what fixed it.

---

### Chunk 5 — `13-iio-practice-gap.txt` (blog, 683 chars)

**Breadcrumb:** `interviewing.io — the technical interview practice gap`

```
In a previous post, we talked about how women quit interview practice 7 times more often than men after just one bad interview. It's not too much of a leap to say that this is probably happening to any number of groups who are underrepresented/underserved by the current system. In other words, though it's a broken process for everyone, the flaws within the system hit these groups the hardest—just because they haven't had the chance to internalize exactly how much of technical interviewing is a game. Sadly, since we've started running our Fellowship program for engineers from underrepresented backgrounds, we've seen this effect firsthand.

The technical interview practice gap
```

**Standalone test: passes with one caveat.** The 7× claim is stated with its comparison group and
condition ("after just one bad interview"), so it is checkable. The caveat is the opening phrase
"In a previous post" — a reference to a source outside this chunk and outside the corpus, so the
underlying study cannot be verified from the retrieved context. A grounded answer citing this figure
should attribute it to interviewing.io's summary rather than to primary data. Same trailing-heading
artifact as Chunk 3.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, run locally. 384 dimensions, ~256
word-piece input limit (this is the constraint that set the 800-character chunk-size ceiling in the
Chunking Strategy section — anything longer is silently truncated before embedding). Text embedded
is the heading breadcrumb plus the chunk body, not the chunk alone, so a chunk about "Rora" carries
the heading path that identifies Rora as a negotiation service.

Chosen for one practical reason: it runs offline with no API key, no per-query cost, and no rate
limit, which matters for an iterate-and-re-embed workflow like this project's — the index was
rebuilt more than a dozen times while tuning chunk size and overlap.

**Production tradeoff reflection.** If this were deployed for real users and cost were not a
constraint, in order of what actually caused friction while building this system:

1. **Context length.** The 256 word-piece limit is what forced the 800-character chunk ceiling,
   which in turn forced the paragraph→sentence→hard-cut fallback ladder described in Chunking
   Strategy. A model with an 8k context window (OpenAI `text-embedding-3-large`, Voyage, Cohere
   Embed v3) would let a chunk be an entire thread or guide section, removing most of that
   complexity in one move.
2. **Domain vocabulary.** Measured directly: `all-MiniLM-L6-v2` places "Is Blind 75 enough
   preparation?" only 0.464 cosine-similar to its plain-English paraphrase ("Is a curated list of 75
   practice problems enough preparation?"). The model was trained on general web text and only
   partially knows this domain's jargon (`E5`, `Blind 75`, `tight loop`). A hybrid retriever that
   adds keyword (BM25) matching alongside semantic search would catch exact jargon a pure embedding
   model misses.
3. **Asymmetric retrieval.** Matching a short question to a long passage is a different task from
   comparing two similar-length sentences, which is closer to what this model was trained on. A
   model with explicit query/passage prefixes (E5, BGE) is built for exactly this asymmetry. Tested
   the more obvious fix — `multi-qa-MiniLM-L6-cos-v1`, trained specifically for question→passage
   retrieval — and it made the out-of-scope refusal problem *worse*, not better: it correctly
   identified negotiation advice as the best available answer to a mortgage-negotiation question,
   which is the right behaviour for the training objective and the wrong one for this system. The
   lesson generalizes: a "better" retrieval model can sharpen a false positive as readily as a true
   one, so any embedding-model swap needs to be measured against out-of-scope controls, not just
   against the target queries.
4. **Latency and privacy.** Local embedding costs nothing per query and sends no user question to a
   third party. An API-hosted model adds network latency and a data-sharing surface — a reasonable
   trade for a product at scale, not for this project.
5. **Multilingual support.** Not a live need — the corpus is entirely English — though
   `system-design-primer` ships translated READMEs, whose language-switcher rows are exactly what
   the non-prose chunk filter (Chunking Strategy) exists to drop.

---

## Retrieval Test Results

<!-- Run these 3 queries through your retrieval system and record the top returned chunks.
     For at least 2 of the 3, explain why the returned chunks are relevant to the query.
     Results must be text — not screenshots. -->

Produced by `test_retrieval.py` against the 868-chunk ChromaDB index. Scores are cosine similarity
(Chroma returns distance; similarity = 1 − distance). Settings: `top_k = 5`,
`MAX_PER_SOURCE = 2`, `RELEVANCE_FLOOR = 0.35`.

**Query 1:** *"How many LeetCode problems did someone solve before passing a FAANG interview?"*

Top returned chunks:
- **0.674** `16-marchenko-postmortem.txt` — "My preparation for Coding interviews. As an example, I have solved a total of **175 LeetCode tasks (52 easy, 106 medium, 17 hard)** (some tasks I have already solved 3+ times)…"
- **0.624** `12-iio-600-interviews.txt` — "I've conducted over 600 technical interviews on interviewing.io. Here are 5 common problem areas I've seen…"
- **0.619** `12-iio-600-interviews.txt` — "Technical Proficiency. In this category, I grade a candidate on how proficient they seem in their language of choice…"
- **0.604** `16-marchenko-postmortem.txt` — "Read and understand the task. Also, ask questions about constraints and edge cases…"
- **0.578** `05-coding-rubrics.txt` — "Basic problem solving signals: Understands the problem quickly by asking good clarifying questions…"

Relevance explanation: rank 1 is the exact verified answer, and it carries the total *and* its
difficulty breakdown in a single sentence — the split that an earlier 400-character chunk size had
severed. Ranks 2–3 are semantically reasonable but wrong in a specific and instructive way: "600
technical interviews" is a *count of interviews conducted by an interviewer*, not problems solved by
a candidate. The embedding model matches on topic (large counts, interview practice) and cannot tell
the two quantities apart, which is the "numbers are weak signals" limitation recorded in
planning.md. Ranks 4–5 shift to interview technique rather than volume. Only rank 1 answers the
question, so `top_k = 5` is doing real work here — a stricter floor would not have helped, since the
distractors score close to the answer.

---

**Query 2:** *"How difficult are the LeetCode questions for entry level roles, and do interviewers give hints?"*

Top returned chunks:
- **0.737** `18-levels-newgrad-expedia.txt` — opening post + reply: "…noticed **most leetcode style questions are usually mediums**. As long as you are explaining your thought process… they will usually **guide you in the right direction, or maybe even a hint**"
- **0.695** `18-levels-newgrad-expedia.txt` — same opening post, adjacent replies (market conditions, AI interview tools)
- **0.599** `23-hn-ai-killed-interview.txt` — "[jarsin] I never understood why Big Tech never setup contracts with all the SAT and ACT test centers…"
- **0.579** `23-hn-ai-killed-interview.txt` — further replies from the same discussion
- **0.570** `01-swe-interview-guide.txt` — "Frequency: Occasional. Quizzes are meant to be a first-pass filter as a quick and dirty way of weeding out extremely weak candidates…"

Relevance explanation: rank 1 answers **both halves** of the question in one chunk — difficulty
("usually mediums") and hints ("guide you in the right direction, or maybe even a hint") — which is
the case for keeping forum threads together rather than splitting them per reply. Note the visible
effect of `MAX_PER_SOURCE = 2`: before that cap, all five slots were filled by this one thread, each
repeating the same prepended opening post, so five results delivered one document's worth of
information. The cap forces ranks 3–5 to come from other sources.

This query is also the corpus's known **attribution trap**. The thread names Expedia, Blue Origin
and eBay, and no reply mentions any of them, so a system that dropped the opening post could
attribute "usually mediums" to Expedia specifically. Because the question is prepended to every
chunk, the retrieved context makes the mismatch visible.

---

**Query 3 (out-of-scope control):** *"What are good interview questions for a nursing job?"*

Top returned chunks:
- **0.460** `12-iio-600-interviews.txt` — "I also have a daily email series covering several kinds of interview questions…"
- **0.440** `02-behavioral-interview.txt` — "…there are three questions that are very very common and it's worth preparing for…"
- **0.424** `03-behavioral-questions.txt` — Airbnb-specific behavioural questions
- **0.419** `12-iio-600-interviews.txt` — "If you have strong opinions about interviewing or hiring that you've been itching to write about…"
- **0.413** `06-behavioral-rubrics.txt` — "Below are questions and answers illustrating how interviewers collect signals…"

Relevance explanation: **every one of these is irrelevant, and all five clear the relevance floor.**
This is the deliberately hardest control case. The query shares its entire surface shape with the
corpus — "interview questions", "job" — and differs only in profession, which the embedding model
has no way to weight as decisive. At **0.460** it outscores *every* abstractly-phrased in-domain
question tested, including "Should I take the first offer?" (0.451) and "Is grinding LeetCode worth
the time?" (0.461, within noise).

This is the measurement that determined the architecture: **no single similarity threshold can
separate in-scope from out-of-scope on this corpus** (window = −0.009). An earlier floor of 0.48,
tuned against only the five factual evaluation questions, looked fine on those and falsely refused
"Is grinding LeetCode worth the time?". The floor was therefore lowered to 0.35, where it rejects
only the unambiguously unrelated — "What is the capital of Australia?" (0.161), "How do I fix a
leaking kitchen tap?" (0.185) — and refusal for adjacent domains is delegated to the grounding
prompt, which can read that software-engineering interview advice does not answer a nursing question.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction** (full text in `answer.py`, `SYSTEM_PROMPT`):

```
You are a research assistant answering questions about software engineering
interview preparation. You answer ONLY from the numbered SOURCES supplied in
the user message. You have no other knowledge available to you for this task.

Rules, in order of priority:

1. GROUND EVERY CLAIM. After each factual statement, cite the source it came
from as [S1], [S2], etc. A statement with no citation is not allowed.

2. REFUSE WHEN THE SOURCES DO NOT ANSWER THE QUESTION. If the sources are
about a different subject than the question asks about, say exactly what you
do and do not have... This applies even when the sources are on an adjacent
topic that shares vocabulary with the question -- for example, sources about
software engineering interviews do not answer a question about nursing
interviews, and sources about salary negotiation do not answer a question
about mortgage or rent negotiation.

3. REPORT DISAGREEMENT, DO NOT RESOLVE IT. If two sources conflict, say so
and attribute each position... Do not average them.

4. DO NOT GENERALISE FROM A NARROWER SOURCE. If the question names a
specific company and the sources discuss interviewing generally, say the
sources do not cover that company specifically.

5. FLAG AGE WHEN IT MATTERS.

6. QUOTE NUMBERS EXACTLY as they appear.
```

Rule 2's explicit adjacent-domain examples exist because a relevance-score cutoff alone cannot make
this decision: measured on the real index, "What are good interview questions for a nursing job?"
scores **0.460** best-match similarity, which is *higher* than the legitimate in-domain question
"Should I take the first offer?" at 0.451. The two bands overlap (window = −0.009 across 10
in-domain and 6 out-of-domain test questions), so no single number distinguishes them. Grounding is
therefore enforced in **three places, not one**:

1. **Retrieval floor** (`RELEVANCE_FLOOR = 0.35` in `query_index.py`) — a cheap pre-filter that
   rejects only queries with no plausible relationship to the corpus at all (e.g. "capital of
   Australia" scores 0.161). If nothing clears it, the LLM is never called, and the refusal is
   generated directly from the retrieval scores.
2. **Context structure** — retrieved chunks are numbered `[S1]`…`[Sk]` and each is labelled with
   its source type, title, section heading, URL and similarity score before being handed to the
   model (`answer.py`, `build_context()`). This is what makes per-claim citation and disagreement
   detection possible — the model is shown *which* source said what, not one undifferentiated block
   of text.
3. **The system prompt itself** — the only stage that can catch an adjacent-domain question, because
   deciding "this shares vocabulary but is a different topic" requires reading the text, which a
   cosine distance cannot do.

**How source attribution is surfaced in the response.** Every factual sentence in the model's answer
must carry an inline `[S1]`-style citation (enforced by prompt rule 1, spot-checked in the
Evaluation Report below). Below the answer, `format_sources()` prints a numbered list matching each
`[Sn]` to its title, source type, similarity score, filename + position within that document, and
URL — so a citation can be followed back to the exact retrieved passage, not just to a document
name.

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query: *"How many LeetCode problems did someone solve before passing a FAANG interview, and what was the difficulty split?"*

Response:
> He solved 175 LeetCode problems in total, broken down as 52 easy, 106 medium, and 17 hard tasks before passing his FAANG interview [S1].

Source attribution: `[S1]` Andrei Marchenko — Cracking the FAANG interview (2024), blog, similarity 0.666, `documents/16-marchenko-postmortem.txt`, chunk 21/34, https://amarchenko.dev/blog/2024-01-17-interview-experience/

---

**Grounded response 2**

Query: *"Is the first offer a company gives the best package they can offer?"*

Response:
> No. According to the Tech Interview Handbook's negotiation guide, "The initial offer that you are given is never the best package that the company can offer" — the guide advises that most offers have room for negotiation and you can usually improve the terms [S2].

Source attribution: `[S2]` Tech Interview Handbook — negotiation, guide, similarity 0.516, `documents/07-negotiation.txt`, chunk 1/8, https://raw.githubusercontent.com/yangshun/tech-interview-handbook/main/apps/website/contents/negotiation.md
(Retrieval returned `08-negotiation-rules.txt` at higher similarity as `[S1]`, but the model correctly attributed the exact quoted claim to `[S2]`, the source that actually contains that sentence — a check worth doing explicitly, since a citation to the wrong same-topic source would not otherwise be obvious.)

---

**Out-of-scope query**

Query: *"What is the best way to negotiate a mortgage rate?"*

System response (refusal):
> My sources don't cover this. They discuss negotiating job offers, compensation expectations, and negotiation services for tech positions, not how to negotiate a mortgage rate.

This is the hardest realistic refusal case, not the easiest: the query scores 0.440 similarity
against the corpus (well above the 0.35 retrieval floor, so the LLM *is* called) because
"negotiate" is genuinely shared vocabulary with the negotiation sources. Refusal here is produced
entirely by prompt rule 2 reading the retrieved text, not by the retrieval floor.

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:** A single free-text question box (Gradio, `app.py`). Also usable directly from the
command line: `.venv/bin/python answer.py "<question>"`. Both call the same `answer()` function in
`answer.py`, so behaviour is identical regardless of interface.

**Output format:** A Markdown-rendered answer with inline `[S1]`-style citations, followed by a
numbered source list — for each cited source: title, source type, similarity score, filename,
chunk position within its document, and URL. If nothing clears the relevance floor, the answer area
shows the refusal text and the source list is replaced with a note naming which stage refused.

Run the interface with `.venv/bin/python app.py`, which opens a local Gradio page at
`http://127.0.0.1:7860`.

---

**Sample Interaction Transcript**

> **User:** How difficult are the LeetCode questions in entry-level interviews, and do interviewers give hints?

> **System:**
> The experience shared in the Levels.fyi thread notes that entry-level LeetCode-style questions are **typically of medium difficulty**. Interviewers usually **listen to your thought process** and will often **guide you toward a solution or even give a hint** if you're stuck [S1].
>
> **Sources**
> ```
> [S1] Levels.fyi — New grad interview experience (Expedia Group, Blue Origin, eBay)  (thread, sim 0.727)
>       18-levels-newgrad-expedia.txt chunk 4/6
>       https://www.levels.fyi/community/thread/1LBjuA/new-grad-interview-experience--expedia-group-blue-origin-ebay
> [S2] (same thread, chunk 0/6)
> [S3] Hacker News — AI killed the tech interview. Now what?  (thread, sim 0.599)
> [S4] Tech Interview Handbook — SWE interview guide  (guide, sim 0.579)
> [S5] Hacker News — AI killed the tech interview. Now what?  (thread, sim 0.570)
> ```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

Run via `.venv/bin/python run_eval.py`, which calls the live pipeline (retrieval + Groq generation)
for each question. Full transcripts in that script's output; summarized here.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How many LeetCode problems did an engineer report solving before passing a FAANG interview, and what was the difficulty split? | 175 total — 52 easy, 106 medium, 17 hard | "He solved 175 LeetCode problems in total, broken down as 52 easy, 106 medium, and 17 hard tasks before passing his FAANG interview [S1]." | Relevant (top-1 sim 0.666, correct source ranked #1) | Accurate |
| 2 | What share of recruiting leaders are conducting interviews in person to combat candidate fraud? | 72.4% | "According to a recent Gartner survey, 72.4% of recruiting leaders say they are now conducting interviews in-person to combat candidate fraud [S1][S2]." | Relevant (top-1 sim 0.736, correct source ranked #1) | Accurate |
| 3 | What difficulty are LeetCode questions in entry-level interviews, and do interviewers give hints? | Mostly mediums; interviewers usually guide you or give a hint | "...entry-level LeetCode-style questions are typically of medium difficulty. Interviewers usually listen to your thought process and will often guide you toward a solution or even give a hint if you're stuck [S1]." | Relevant (top-1 sim 0.727, correct source ranked #1) | Accurate |
| 4 | Is the first offer a company gives the best package they can offer? | No — the initial offer is never the best package | "No. ... 'The initial offer that you are given is never the best package that the company can offer' — the guide advises... you can usually improve the terms [S2]." | Relevant (correct source at rank #2, sim 0.516; a same-topic sibling source, `08-negotiation-rules.txt`, ranked #1 at 0.542) | Accurate — and the model correctly attributed the exact quoted claim to the source that actually contains it, not to the higher-ranked sibling |
| 5 | How much more often do women abandon interview practice than men after a single bad interview? | 7 times more often | "Women quit interview practice about 7 times more often than men after just one bad interview — as reported in both the 'technical interview practice gap' post and the 'interview performance is kind of arbitrary' post [S1][S2]." | Relevant (top-1 sim 0.702) | **Partially accurate** — the "7 times" figure is correct, but "reported in both posts" overstates independent corroboration: `11-iio-arbitrary.txt` and `13-iio-practice-gap.txt` contain the **identical sentence** ("In a previous post, we talked about how women quit interview practice 7 times more often...") because one interviewing.io post is referencing the other, not because two separate studies converged on the number. The system had no way to detect this — both chunks score 0.665, are literally the same text, and nothing in the metadata marks one as a self-citation of the other. |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary: 4/5 fully accurate, 1/5 partially accurate. 5/5 retrieval relevant.** The one downgrade
is a subtler failure than a wrong number — it is a true fact presented with slightly overstated
evidentiary weight, catchable only by reading the cited sources closely enough to notice they share
a sentence verbatim.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** *"What was the Expedia new grad software engineer interview like?"* — not
one of the five official evaluation questions, but a probe deliberately built from a corpus defect
found while chunking (`planning.md`, Anticipated Challenges #1).

**What the system returned:**
> "The thread that discusses the Expedia Group new-grad interview only contains a brief comment
> about the interview style. One respondent notes that 'they will likely be looking more to your
> explanations and do more in-person interviews' [S1]. No other details about the difficulty of the
> coding (LeetCode) questions, whether interviewers give hints, or the exact structure of the
> process are provided in the sources."

**Root cause, tied to a specific pipeline stage — generation, not retrieval.** Retrieval did its job
correctly: it found `18-levels-newgrad-expedia.txt` at similarity 0.721 and ranked it first. The
underlying corpus defect is real — this thread's title names Expedia, Blue Origin and eBay, and
**none of its six replies mentions any of the three companies**; the quoted reply is generic
commentary about AI tools and the hiring market in general. Chunking already defends against this
by prepending the thread's opening post (which names the companies) to every reply chunk
(`chunk_documents.py`, thread policy), specifically so the model can see that a reply doesn't
actually address the question.

That defense partially worked and partially backfired. It worked in that the model did not invent
LeetCode-difficulty or hint-giving details for Expedia — it correctly said no such details exist.
But it backfired in framing: by calling this "the thread that discusses the Expedia Group new-grad
interview" and describing the quoted reply as being "about the interview style," the response
implies the reply characterizes Expedia's process specifically, when the reply never says anything
company-specific at all. The system prompt's rule 4 ("do not generalise from a narrower source")
tells the model not to attribute general claims to a named company, but the instruction is not
precise enough to stop the *thread-level* framing from doing exactly that by proximity — the reply
sits inside a chunk whose opening post names Expedia, and the model treated "in this Expedia thread"
as loosely equivalent to "about Expedia," which they are not.

This is worth stating plainly: **grounding was structurally correct (every claim traces to a real
retrieved chunk) and still misleading**, because grounding guarantees a citation exists, not that
the cited text supports the specific attribution the sentence around it implies. A grader — or a
job-seeking user — reading only the response's first sentence would come away believing the corpus
says something specific about Expedia's interview style. It does not.

**What I would change to fix it:** Two independent fixes, addressing retrieval and generation
separately since this is a compound problem:

1. **Generation**: sharpen the system prompt with this exact scenario as a worked example — instead
   of the general "do not generalise" rule, an explicit instruction to check whether a reply's own
   text names the entity the question asks about, and if not, say the *reply* (not just "the
   sources" in the abstract) does not address it by name.
2. **Chunking/retrieval**: tag, in chunk metadata, whether a reply's own text contains any of the
   named entities from its thread's opening post. A chunk lacking that overlap could be surfaced to
   generation with an explicit flag ("this reply does not itself mention: Expedia, Blue Origin,
   eBay"), turning a fact the pipeline already knows (retrieval computed the opening post
   separately from the reply) into a signal generation can act on, rather than relying on the LLM to
   notice it unprompted.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Chunking Strategy section
*before* touching code forced a decision — 800 characters, 300 overlap — that later turned out to
be wrong on the first try (400/200 made packing completely inert; verified directly: 0 of 879
chunks ever merged more than one paragraph), but having a stated number and a stated reason meant
the failure was measurable rather than a vague "chunks look off." Every subsequent fix in this
project followed the same shape: state a number in planning.md, measure it against the real corpus,
and correct the document when the measurement disagreed with the guess. Without the spec's insistence
on committing to specific numbers up front, tuning would have had no baseline to compare against.

**One way your implementation diverged from the spec, and why:** The spec's guiding questions frame
the relevance floor as something you tune once against a handful of queries. In practice, a floor
tuned against only the five evaluation questions (0.48) looked correct — worst in-scope score 0.542
vs best out-of-scope 0.440 — and then **falsely refused** a legitimate in-domain question ("Is
grinding LeetCode worth the time?", 0.461) once tested against a wider set. Widening the test to 10
in-domain and 6 out-of-domain questions showed the two bands overlap entirely (window = −0.009), so
no single threshold can carry the scope decision. The implementation diverged from a single-floor
design to a two-stage one: a low floor (0.35) that rejects only the unambiguously unrelated, with
the system prompt handling adjacent-domain refusal by reading the retrieved text. This wasn't a
spec failure — the spec's own guiding question ("what happens if you retrieve too few / too many")
is what prompted testing beyond the five questions in the first place — but the single-cutoff
design it implies did not survive contact with this corpus's vocabulary overlap between adjacent
domains (negotiation, interviewing).

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — chunking parameters, wrong on the first try**

- *What I gave the AI:* the embedding model's ~256 word-piece truncation limit, and an instruction
  to scaffold `chunk_documents.py` with the packing function left as a `TODO` for me to implement
  myself rather than write it wholesale — I wanted to write the actual decision-carrying code.
- *What it produced:* a working scaffold, plus an initial suggested chunk size of 400 characters
  with 200 overlap ("guidance, not answers" — explicitly a starting guess, not a final number).
- *What I changed or overrode:* after implementing and running the packer, the diagnostic output
  showed 0 of 879 chunks ever merged more than one paragraph — 400 chars was smaller than most
  individual paragraphs (median 266, many longer), so nothing ever got combined. I raised the
  target to 800 and the overlap to 300 after measuring the actual paragraph-length distribution in
  my documents, rather than accepting either the AI's first guess or an arbitrary round number.

**Instance 2 — a content filter that deleted the wrong thing**

- *What I gave the AI:* the observation that `system-design-primer` (one of my 24 sources) contains
  markdown tables and a table of contents that are pure link lists, and an instruction to filter
  chunks like that out of the index.
- *What it produced:* a first-pass rule that dropped any chunk where most lines started with `|`
  (a markdown table row). It ran without errors and reported "50 chunks dropped as non-prose."
- *What I changed or overrode:* rather than trust the count, I read the printed samples of what got
  dropped — and the rule had also deleted the coding-interview-rubrics scoring table and the
  study-plan priority table from two entirely different source documents, which are genuine content,
  not navigation. I had the AI replace the rule with one that measures the fraction of a chunk's
  characters that are link markup specifically (URLs, markdown link targets) rather than table
  syntax generally, and we validated the new threshold by measuring the actual separation between
  content tables (0.05–0.74) and link tables (0.81–0.99) in my corpus before trusting it. Reading the
  dropped samples, not the count, is what caught this — a count alone looked fine.
