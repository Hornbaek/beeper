# app.py

import streamlit as st
import json

# --- Load Knowledgebase ---
@st.cache_data
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data("beekeeping_knowledgebase.json")

# --- UI ---
st.title("🐝 Beekeeper Knowledgebase Explorer")

query = st.text_input("Search topics, summaries, or URLs:")

if query:
    results = [entry for entry in data if query.lower() in entry["summary"].lower() or
               any(query.lower() in topic.lower() for topic in entry["topics"]) or
               query.lower() in entry["url"].lower()]
else:
    results = data

st.write(f"Found {len(results)} results.")

for entry in results:
    st.subheader(entry["title"])
    st.write(f"**URL**: {entry['url']}")
    st.write(f"**Topics**: {', '.join(entry['topics'])}")
    st.write(f"**Summary**: {entry['summary']}")
    st.write(f"**Source Type**: {entry['source_type']}  |  **Quality**: {entry['quality_score']}⭐")
    st.write(f"**Published**: {entry['date_published']}")
    st.markdown("---")
