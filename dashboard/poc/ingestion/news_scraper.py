import urllib.parse
from datetime import datetime
# pyrefly: ignore [missing-import]
import feedparser
import streamlit as st

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_news_data(keyword: str, max_results: int = 20) -> list[dict]:
    try:
        query = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
        
        feed = feedparser.parse(rss_url)
        
        results = []
        for idx, entry in enumerate(feed.entries[:max_results]):
            source_name = getattr(entry, "source", {}).get("title", "Berita Online")
            pub_date = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Simple content extraction
            content = entry.title
            
            results.append({
                "post_id": f"NEWS-{idx}-{hash(entry.link) % 10000}",
                "platform": "Berita Online",
                "author": source_name,
                "handle": "@news",
                "created_at": pub_date,
                "content": content,
                "url": entry.link
            })
            
        return results
    except Exception as e:
        print(f"Error fetching News data: {e}")
        return []
