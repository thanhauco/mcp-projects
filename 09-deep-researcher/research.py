
from typing import List, Dict
import httpx, re
from bs4 import BeautifulSoup
from readability import Document
from markdownify import markdownify as md

def simple_search(query: str, num: int = 5) -> List[Dict]:
    # Very basic metasearch against DuckDuckGo HTML (no API key). May fail if blocked.
    url = "https://duckduckgo.com/html/"
    params = {"q": query}
    r = httpx.post(url, data=params, timeout=30.0, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.select("a.result__a")[:num]:
        results.append({"title": a.get_text(strip=True), "url": a["href"]})
    return results

def fetch_readable(url: str) -> Dict:
    r = httpx.get(url, timeout=30.0, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    doc = Document(r.text)
    html = doc.summary()
    text_md = md(html)
    return {"title": doc.short_title() or url, "markdown": text_md}
