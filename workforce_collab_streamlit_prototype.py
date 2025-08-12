import streamlit as st
from openai import OpenAI
import os

st.title("Workforce Collaboration Roadmap Generator")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

categories = [
    "Correspondence",
    "Document Collaboration",
    "Communications",
    "Workflow Architecture",
    "Personal Compute",
    "Workforce Connectivity",
    "Identity Management",
    "Corporate Communications"
]

notes = {}
for category in categories:
    notes[category] = st.text_area(f"Technical Notes for {category}")

if st.button("Generate All"):
    with st.spinner("Generating roadmap and summaries..."):
        for category in categories:
            user_notes = notes[category].strip()

            if not user_notes:
                continue  # skip empty sections

            # CEO Summary
            ceo_prompt = (
                f"Below are improvement opportunities under my workforce collaboration "
                f"'{category}' area:\n\n{user_notes}\n\n"
                f"From the standpoint of a CEO, why does this matter? "
                f"What will it accomplish for the organization?"
            )
            ceo_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in executive communications."},
                    {"role": "user", "content": ceo_prompt}
                ]
            )
            ceo_summary = ceo_resp.choices[0].message.content
            st.subheader(f"CEO Summary for {category}")
            st.write(ceo_summary)

            # CIO Talking Points (based on CEO Summary)
            cio_prompt = (
                f"For the following CEO summary, add outcomes/value statements as talking points "
                f"a CIO could use to sell the idea of committing to these projects:\n\n{ceo_summary}"
            )
            cio_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in IT leadership and strategy."},
                    {"role": "user", "content": cio_prompt}
                ]
            )
            cio_talking_points = cio_resp.choices[0].message.content
            st.subheader(f"CIO Talking Points for {category}")
            st.write(cio_talking_points)

st.success("Ready to generate!")
