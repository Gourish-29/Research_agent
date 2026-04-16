import streamlit as st
import os
from openai import OpenAI
from duckduckgo_search import DDGS
import requests

# --- Setup ---
st.title("Multi-Agent AI Researcher 🔍🤖")
st.caption("Research HackerNews and generate summaries using AI")

# Secure API key (no manual input)
api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# --- Functions ---

# Get top HackerNews stories
def get_hn_stories(query):
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": query, "tags": "story", "hitsPerPage": 5}
    res = requests.get(url, params=params).json()
    
    stories = []
    for item in res["hits"]:
        stories.append({
            "title": item["title"],
            "url": item.get("url", ""),
        })
    return stories


# Web search
def web_search(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(r["href"])
    return results


# Generate summary using OpenAI
def generate_summary(query, stories, links):
    content = f"""
    Query: {query}

    HackerNews Stories:
    {stories}

    Extra Links:
    {links}

    Write a structured article with:
    - Title
    - Summary
    - Key Insights
    - References
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
    )

    return response.choices[0].message.content


# --- UI ---
query = st.text_input("Enter your research query")

if query:
    with st.spinner("Researching..."):
        stories = get_hn_stories(query)
        links = web_search(query)
        result = generate_summary(query, stories, links)

        st.markdown(result)