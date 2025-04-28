# research.py

import os
from dotenv import load_dotenv
load_dotenv()

from serpapi import GoogleSearch


def search_links(query: str, num_results: int = 20) -> list:
    """Search Google using SerpAPI and return a list of URLs."""
    api_key = os.getenv("SERPAPI_API_KEY")  # <-- Load from environment variable (best)
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not set in environment variables.")

    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    links = []
    for r in results.get('organic_results', []):
        if 'link' in r:
            links.append(r['link'])
    return links
