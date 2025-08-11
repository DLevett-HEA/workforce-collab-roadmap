import os
import streamlit as st
from openai import OpenAI
from openai.error import RateLimitError
import re

# Initialize OpenAI client
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

st.set_page_config(page_title="Workforce Collaboration Roadmap", layout="wide")
st.title("Workforce Collaboration Roadmap & Executive Messaging")

st.markdown(
    "Enter your technical notes below for each category. Click **Generate All** to produce a combined AI roadmap, CEO summary, and CIO talking points."
)

# Collect notes for all categories
notes_by_category = {}
cols = st.columns(2)
for i, category in enumerate(CATEGORIES):
    with cols[i % 2]:
        notes_by_category[category] = st.text_area(f"Technical Notes — {category}", height=130)

@st.cache_data(show_spinner=False)
def get_ai_response(prompt: str, model: str = "gpt-4o") -> str:
    try:
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
    except RateLimitError:
        return "[Error] OpenAI rate limit exceeded. Please try again later."
    except Exception as e:
        return f"[Error] Unexpected error: {e}"

def build_combined_prompt(notes_by_cat: dict) -> str:
    intro = (
        "You are an enterprise IT strategy assistant. For each category below, produce three labeled sections:\n"
        "1) Roadmap: an actionable, prioritized roadmap.\n"
        "2) CEO Summary: why this category matters to the CEO.\n"
        "3) CIO Talking Points: 2-3 concise bullets the CIO can use to sell the concept.\n\n"
        "Please return your response with clear section headers as:\n"
        "\"Category: <category name>\",\n"
        "\"Roadmap:\", \"CEO Summary:\", \"CIO Talking Points:\"\n\n"
        "Here are the categories and their technical notes:\n"
    )
    body = ""
    for cat, notes in notes_by_cat.items():
        body += f"\nCategory: {cat}\nTechnical Notes:\n{notes}\n"

    return intro + body + "\n\nRespond clearly with labeled sections."

def parse_ai_response(response: str) -> dict:
    # Parse the combined response into a nested dict by category and section
    # Expected format:
    # Category: Correspondence
    # Roadmap:
    # ...
    # CEO Summary:
    # ...
    # CIO Talking Points:
    # ...
    # Category: Document Collaboration
    # ...

    results = {}
    current_category = None
    current_section = None

    section_headers = {"Roadmap", "CEO Summary", "CIO Talking Points"}

    lines = response.splitlines()
    for line in lines:
        line_strip = line.strip()
        cat_match = re.match(r"Category:\s*(.*)", line_strip)
        if cat_match:
            current_category = cat_match.group(1).strip()
            results[current_category] = {"Roadmap": "", "CEO Summary": "", "CIO Talking Points": ""}
            current_section = None
            continue
        elif line_strip in section_headers:
            current_section = line_strip
            continue
        elif current_category and current_section:
            results[current_category][current_section] += line + "\n"

    # Clean up whitespace
    for cat in results:
        for sec in results[cat]:
            results[cat][sec] = results[cat][sec].strip()

    return results

if st.button("Generate All"):
    prompt = build_combined_prompt(notes_by_category)
    with st.spinner("Generating AI roadmap and summaries..."):
        ai_response = get_ai_response(prompt)
    if ai_response.startswith("[Error]"):
        st.error(ai_response)
    else:
        parsed = parse_ai_response(ai_response)

        for category in CATEGORIES:
            st.markdown(f"---\n## {category}")
            roadmap = parsed.get(category, {}).get("Roadmap", "*No roadmap generated.*")
            ceo = parsed.get(category, {}).get("CEO Summary", "*No CEO summary generated.*")
            cio = parsed.get(category, {}).get("CIO Talking Points", "*No CIO talking points generated.*")

            c1, c2, c3 = st.columns(3)
            c1.markdown("**Roadmap**")
            c1.text_area(f"Roadmap — {category}", value=roadmap, height=150, key=f"roadmap__{category}")
            c2.markdown("**CEO Summary**")
            c2.text_area(f"CEO Summary — {category}", value=ceo, height=100, key=f"ceo__{category}")
            c3.markdown("**CIO Talking Points**")
            c3.text_area(f"CIO Talking Points — {category}", value=cio, height=150, key=f"cio__{category}")

st.markdown(
    "\n---\n*Make sure your OpenAI API key is set in your environment or Streamlit Secrets as `OPENAI_API_KEY`.*"
)
