import os
import streamlit as st
from openai import OpenAI
from typing import Dict
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

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

def build_combined_prompt(notes_by_category: Dict[str, str]) -> str:
    intro = """
You are an enterprise IT strategy assistant. For each category below, produce three labeled sections:
1) Roadmap: an actionable, prioritized roadmap (steps, rough order, and estimated outcomes).
2) CEO Summary: a 2-3 sentence explanation of why this category matters to the CEO and the value it provides the organization.
3) CIO Talking Points: 2-3 concise bullets the CIO can use to sell the concept to leadership.

Return your response with clear headers exactly as:
Category: <category>
Roadmap:
CEO Summary:
CIO Talking Points:

Here are the categories and their technical notes:
"""
    body = ""
    for category, notes in notes_by_category.items():
        body += f"\nCategory: {category}\nTechnical Notes:\n{notes}\n"
    return intro + body + "\n\nRespond with clear labeled sections."

@st.cache_data(show_spinner=False)
def get_ai_response(prompt: str, model: str = "gpt-4o") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise, professional enterprise IT strategy assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1600,
    )
    return response.choices[0].message.content.strip()

def parse_combined_response(response: str) -> Dict[str, Dict[str, str]]:
    results = {}
    current_category = None
    current_section = None
    section_headers = {"Roadmap", "CEO Summary", "CIO Talking Points"}

    lines = response.splitlines()
    for line in lines:
        line = line.strip()
        cat_match = re.match(r"Category:\s*(.*)", line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            results[current_category] = {"Roadmap": "", "CEO Summary": "", "CIO Talking Points": ""}
            current_section = None
            continue
        elif line in section_headers:
            current_section = line
            continue
        elif current_category and current_section:
            results[current_category][current_section] += line + "\n"

    # Strip whitespace
    for cat in results:
        for sec in results[cat]:
            results[cat][sec] = results[cat][sec].strip()

    return results

# --- Streamlit UI ---

st.title("Workforce Collaboration — Roadmap & Executive Messaging")

notes_by_category = {}
cols = st.columns(2)
for i, category in enumerate(CATEGORIES):
    with cols[i % 2]:
        notes_by_category[category] = st.text_area(f"Technical Notes — {category}", height=150)

model = st.selectbox("Model", options=["gpt-4o", "gpt-4.1", "gpt-4o-mini", "gpt-3.5-turbo"], index=0)

if st.button("Generate All"):
    prompt = build_combined_prompt(notes_by_category)
    with st.spinner("Generating AI output..."):
        ai_response = get_ai_response(prompt, model=model)

    if ai_response.startswith("[Error]"):
        st.error(ai_response)
    else:
        parsed = parse_combined_response(ai_response)
        for category in CATEGORIES:
            st.markdown(f"---\n### {category}")
            roadmap = parsed.get(category, {}).get("Roadmap", "*No roadmap generated.*")
            ceo_summary = parsed.get(category, {}).get("CEO Summary", "*No CEO summary generated.*")
            cio_points = parsed.get(category, {}).get("CIO Talking Points", "*No CIO talking points generated.*")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Roadmap**")
                st.text_area(f"Roadmap — {category}", value=roadmap, height=150)
            with c2:
                st.markdown("**CEO Summary**")
                st.text_area(f"CEO Summary — {category}", value=ceo_summary, height=100)
            with c3:
                st.markdown("**CIO Talking Points**")
                st.text_area(f"CIO Talking Points — {category}", value=cio_points, height=150)

st.markdown("---\n*Make sure your OPENAI_API_KEY is set in Streamlit Cloud Secrets or your environment.*")
