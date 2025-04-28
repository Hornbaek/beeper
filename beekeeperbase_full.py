# beekeeperbase_full.py

import os
from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
import openai
import json
import time
from tqdm import tqdm
from typing import List, Dict
from research import search_links


# --- CONFIG ---

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_FETCH_RETRIES = 3
SUMMARIZE_MODEL = "gpt-4"
SAVE_FILENAME = "beekeeping_knowledgebase.json"

# --- FUNCTIONS ---

def fetch_text(url: str) -> Dict:
    """Fetch and clean text, title, and date from a URL."""
    for attempt in range(MAX_FETCH_RETRIES):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Bad status code: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = " ".join(p.get_text() for p in paragraphs)
            title = soup.title.string.strip() if soup.title else "Untitled"
            date_published = "unknown"

            # Try to find date meta tags (basic)
            date_tag = soup.find('meta', {'property': 'article:published_time'}) or \
                       soup.find('meta', {'name': 'date'}) or \
                       soup.find('meta', {'itemprop': 'datePublished'})
            if date_tag and date_tag.get('content'):
                date_published = date_tag['content']

            return {
                "text": text[:6000],
                "title": title,
                "date_published": date_published
            }
        except Exception as e:
            print(f"[Retry {attempt+1}] Error fetching {url}: {e}")
            time.sleep(2)
    print(f"Failed to fetch {url}")
    return {"text": "", "title": "Untitled", "date_published": "unknown"}


def summarize_content(text: str) -> Dict:
    prompt = f"""
You are an expert beekeeping researcher. For the following content:
- Summarize it in 3–6 sentences.
- List 2–5 relevant topics (e.g., hive management, disease control).
- Classify the source type ('scientific paper', 'forum post', 'blog', 'government document', 'other').
- Rate quality 1–5 stars (5=excellent).

Respond in JSON:
{{
  "summary": "...",
  "topics": ["topic1", "topic2"],
  "source_type": "blog",
  "quality_score": 4
}}

CONTENT:
{text}
"""
    try:
        response = openai.ChatCompletion.create(
            model=SUMMARIZE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            timeout=60
        )
        content = response['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error summarizing: {e}")
        return {
            "summary": "Summary unavailable.",
            "topics": [],
            "source_type": "unknown",
            "quality_score": 1
        }

def process_urls(url_list: List[str]) -> List[Dict]:
    results = []
    for url in tqdm(url_list, desc="Processing URLs"):
        page = fetch_text(url)
        if page['text']:
            data = summarize_content(page['text'])
            entry = {
                "title": page.get("title", ""),
                "url": url,
                "summary": data.get("summary", ""),
                "topics": data.get("topics", []),
                "source_type": data.get("source_type", "unknown"),
                "quality_score": data.get("quality_score", 1),
                "date_published": page.get("date_published", "unknown")
            }
            results.append(entry)
    return results

def save_to_json(data: List[Dict], filename: str = SAVE_FILENAME):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} entries to {filename}")

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    research_topic = input("🔎 Enter research topic (e.g., 'hive pest management'): ")
    num_links = int(input("🔗 How many links to fetch (e.g., 10, 20, 50)? "))

    print(f"🌐 Searching links for: {research_topic}")
    urls = search_links(research_topic, num_links)

    print(f"⚙️ Processing {len(urls)} links...")
    knowledgebase = process_urls(urls)

    save_to_json(knowledgebase)
    print("✅ Beekeeper Knowledgebase Ready!")
