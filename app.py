"""Milestone 5: query interface.

Run:  .venv/bin/python app.py
Opens a local Gradio page. One input field (the question), one output area
showing the grounded answer with inline [S1]-style citations followed by a
numbered source list (title, type, similarity score, URL).
"""

import gradio as gr

from answer import answer, format_sources

EXAMPLES = [
    "How many LeetCode problems did someone solve before passing a FAANG interview?",
    "Is the first offer a company gives the best package they can offer?",
    "What is the best way to negotiate a mortgage rate?",
]


def respond(question):
    if not question or not question.strip():
        return "Enter a question above."
    res = answer(question)
    out = f"### Answer\n\n{res['answer']}\n"
    if res["kept"]:
        out += f"\n### Sources\n\n```\n{format_sources(res['kept'])}\n```"
    else:
        out += f"\n*(refused at {res['refused_at']} -- no source cleared the relevance floor)*"
    return out


with gr.Blocks(title="The Unofficial Guide -- SWE Interview Prep") as demo:
    gr.Markdown(
        "# The Unofficial Guide: New-Grad SWE Interview Prep\n"
        "Answers ONLY from a fixed corpus of 24 collected sources (forum threads, "
        "guides, blog posts, one news article). Not a general chatbot -- ask "
        "something outside the corpus and it will say so."
    )
    q = gr.Textbox(label="Your question", placeholder="e.g. Is grinding LeetCode worth it?")
    btn = gr.Button("Ask", variant="primary")
    out = gr.Markdown(label="Response")
    gr.Examples(examples=EXAMPLES, inputs=q)
    btn.click(respond, inputs=q, outputs=out)
    q.submit(respond, inputs=q, outputs=out)

if __name__ == "__main__":
    demo.launch()
