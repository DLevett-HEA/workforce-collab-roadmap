import os
import streamlit as st
from openai import OpenAI
from typing import Dict

# ========== Configuration ==========
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
DEFAULT_MODEL = "gpt-4o"  # Change if needed

CATEGORIES = [
    "Correspondence",
    "Document Collaboration",
    "Communications",
    "Workflow Architecture",
    "Personal Compute",
    "Workforce Connectivity",
    "Identity Management",
    "Corporate Communications",
]

# ========== Helpers ==========

def build_prompt(category: str, notes: str) -> str:
    return f"""
You are an enterprise IT strategy assistant. The user provided technical notes for the category: '{category}'.

Tasks (produce three labeled sections):
1) Roadmap: an actionable, prioritized roadmap (steps, rough order and estimated outcomes).
2) CEO Summary: a 2-3 sentence explanation of why this category matters to the CEO and the value it provides to the organization.
3) CIO Talking Points: 2-3 concise bullets the CIO can use to sell the concept to leadership.

Technical Notes:
{notes}

Return your response with clear section headers exactly as: "Roadmap:", "CEO Summary:", "CIO Talking Points:" so the app can split them.
"""

def call_openai(prompt: str, model: str = DEFAULT_MODEL) -> str:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise, professional enterprise IT strategy assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error calling OpenAI API] {e}"

def split_output(output: str) -> Dict[str, str]:
    sections = {"Roadmap": "", "CEO Summary": "", "CIO Talking Points": ""}
    current = None
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Roadmap:"):
            current = "Roadmap"
            sections[current] += stripped[len("Roadmap:"):].strip() + "\n"
        elif stripped.startswith("CEO Summary:"):
            current = "CEO Summary"
            sections[current] += stripped[len("CEO Summary:"):].strip() + "\n"
        elif stripped.startswith("CIO Talking Points:"):
            current = "CIO Talking Points"
            sections[current] += stripped[len("CIO Talking Points:"):].strip() + "\n"
        elif current:
            sections[current] += line + "\n"
    for k in sections:
        sections[k] = sections[k].strip()
    return sections

# ========== Streamlit UI ==========
st.set_page_config(page_title="Workforce Collaboration Roadmap Assistant", layout="wide")
st.title("Workforce Collaboration — Roadmap & Executive Messaging Prototype")
st.markdown("Enter technical notes per category. Generate an AI roadmap, a CEO summary, and CIO talking points for each category.")

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Settings")
    model = st.selectbox("Model", options=[DEFAULT_MODEL, "gpt-4.1", "gpt-4o-mini", "gpt-3.5-turbo"], index=0)
    auto_generate = st.checkbox("Auto-generate when notes change", value=False)
    gen_button = st.button("Generate All")

with col2:
    st.subheader("Export")
    if st.button("Export All to Markdown"):
        md_lines = ["# Workforce Collaboration Roadmap Export\n"]
        for cat in CATEGORIES:
            notes = st.session_state.get(f"notes__{cat}", "")
            out = st.session_state.get(f"output__{cat}", "")
            md_lines.append(f"## {cat}\n")
            md_lines.append("**Technical Notes:**\n")
            md_lines.append(notes + "\n")
            md_lines.append("**AI Generated:**\n")
            md_lines.append(out + "\n---\n")
        md_blob = "\n".join(md_lines)
        st.download_button("Download Markdown", md_blob, file_name="workforce_collab_roadmap.md", mime="text/markdown")

for category in CATEGORIES:
    st.markdown(f"---\n### {category}")
    notes_key = f"notes__{category}"
    output_key = f"output__{category}"

    if notes_key not in st.session_state:
        st.session_state[notes_key] = ""
    if output_key not in st.session_state:
        st.session_state[output_key] = ""

    notes = st.text_area(f"Technical Notes — {category}", value=st.session_state[notes_key], key=notes_key, height=150)

    should_call = False
    if gen_button:
        should_call = True
    elif auto_generate and st.session_state[notes_key] != "":
        should_call = True

    if should_call:
        with st.spinner(f"Generating AI output for {category}..."):
            prompt = build_prompt(category, st.session_state[notes_key])
            ai_out = call_openai(prompt, model=model)
            st.session_state[output_key] = ai_out

    parsed = split_output(st.session_state.get(output_key, ""))
    r1, r2, r3 = st.columns([1, 1, 1])
    with r1:
        st.markdown("**Roadmap**")
        st.text_area(f"Roadmap — {category}", value=parsed.get("Roadmap", ""), height=150, key=f"roadmap__{category}")
    with r2:
        st.markdown("**CEO Summary**")
        st.text_area(f"CEO Summary — {category}", value=parsed.get("CEO Summary", ""), height=100, key=f"ceo__{category}")
    with r3:
        st.markdown("**CIO Talking Points**")
        st.text_area(f"CIO Talking Points — {category}", value=parsed.get("CIO Talking Points", ""), height=150, key=f"cio__{category}")

st.markdown("---\n**Notes:** Set your OpenAI API key in Streamlit Cloud secrets or as an environment variable named `OPENAI_API_KEY`. Run locally with: `streamlit run workforce_collab_streamlit_prototype.py`")
