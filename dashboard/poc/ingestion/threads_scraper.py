import os
import requests
import streamlit as st
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_threads_data(keyword: str, max_results: int = 20) -> list[dict]:
    """
    Mencari postingan Threads menggunakan Meta Graph API v1.0 (/threads_search)
    Membutuhkan THREADS_ACCESS_TOKEN.
    """
    access_token = os.environ.get("THREADS_ACCESS_TOKEN")
    if not access_token:
        print("THREADS_ACCESS_TOKEN not found. Returning empty list.")
        return []

    url = "https://graph.threads.net/v1.0/threads_search"
    params = {
        "q": keyword,
        "access_token": access_token,
        "search_type": "TOP", 
        "limit": min(max_results, 50)
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("data", [])
        results = []
        
        for item in items[:max_results]:
            # Struktur ini mungkin perlu disesuaikan dengan dokumentasi resmi Threads API
            thread_id = item.get("id", "")
            results.append({
                "post_id": f"TH-{thread_id}",
                "platform": "Threads",
                "author": item.get("username", "Unknown"),
                "handle": f"@{item.get('username', 'Unknown')}",
                "created_at": item.get("timestamp", datetime.now().isoformat()),
                "content": item.get("text", ""),
                "url": item.get("permalink", f"https://www.threads.net/t/{thread_id}"),
                "likes": int(item.get("like_count", 0)),
                "reposts": int(item.get("repost_count", 0)),
                "replies": int(item.get("reply_count", 0)),
            })
            
        return results

    except Exception as e:
        print(f"Error fetching Threads API data: {e}")
        return []

if __name__ == "__main__":
    test_data = fetch_threads_data("Edukasi", 2)
    print("Threads Data:", test_data)
