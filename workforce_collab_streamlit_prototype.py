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
    notes[category] = st.text_area(f"Notes for {category}")

if st.button("Generate All"):
    with st.spinner("Generating roadmap and summaries..."):
        for category in categories:
            user_notes = notes[category]
            if user_notes.strip():
                # Roadmap
                roadmap_prompt = f"Based on these technical notes for {category}, create a roadmap: {user_notes}"
                roadmap_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are an expert in workforce collaboration planning."},
                              {"role": "user", "content": roadmap_prompt}]
                )
                roadmap = roadmap_resp.choices[0].message.content
                st.subheader(f"Roadmap for {category}")
                st.write(roadmap)

                # CEO Summary
                ceo_prompt = f"Explain why {category} is important to a CEO and the value it provides the organization."
                ceo_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are an expert in executive communications."},
                              {"role": "user", "content": ceo_prompt}]
                )
                ceo_summary = ceo_resp.choices[0].message.content
                st.subheader(f"CEO Summary for {category}")
                st.write(ceo_summary)

                # CIO Talking Points
                cio_prompt = f"Take this CEO summary and create 2-3 talking points a CIO could use to sell the concept: {ceo_summary}"
                cio_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are an expert in IT leadership and strategy."},
                              {"role": "user", "content": cio_prompt}]
                )
                cio_talking_points = cio_resp.choices[0].message.content
                st.subheader(f"CIO Talking Points for {category}")
                st.write(cio_talking_points)

st.success("Ready to generate!")
