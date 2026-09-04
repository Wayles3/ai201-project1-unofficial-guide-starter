# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

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

**Model used:**

**Production tradeoff reflection:**

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

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query:

System response (refusal):

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:**

**Output format:**

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
