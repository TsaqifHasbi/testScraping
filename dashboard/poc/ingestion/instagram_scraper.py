import os
import requests
import streamlit as st
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_instagram_data(keyword: str, max_results: int = 20) -> list[dict]:
    """
    Mencari postingan Instagram menggunakan Meta Graph API (Hashtag Search).
    Membutuhkan INSTAGRAM_ACCESS_TOKEN dan INSTAGRAM_USER_ID (ID akun Instagram Business/Creator).
    
    Langkah Graph API:
    1. Cari ID Hashtag berdasarkan nama keyword.
    2. Ambil recent_media menggunakan ID Hashtag tersebut.
    """
    access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
    
    if not access_token or not ig_user_id:
        print("INSTAGRAM_ACCESS_TOKEN atau INSTAGRAM_USER_ID tidak ditemukan. Mengembalikan list kosong.")
        return []

    # Bersihkan hashtag jika ada simbol '#'
    clean_keyword = keyword.replace("#", "")

    try:
        # 1. Dapatkan Hashtag ID
        search_url = "https://graph.facebook.com/v18.0/ig_hashtag_search"
        search_params = {
            "user_id": ig_user_id,
            "q": clean_keyword,
            "access_token": access_token
        }
        
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        hashtag_data = search_response.json()
        
        if not hashtag_data.get("data"):
            return []
            
        hashtag_id = hashtag_data["data"][0]["id"]
        
        # 2. Dapatkan Recent Media dari Hashtag ID
        media_url = f"https://graph.facebook.com/v18.0/{hashtag_id}/recent_media"
        media_params = {
            "user_id": ig_user_id,
            "fields": "id,caption,media_url,permalink,like_count,comments_count,timestamp",
            "limit": min(max_results, 50),
            "access_token": access_token
        }
        
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        media_data = media_response.json()
        
        items = media_data.get("data", [])
        results = []
        
        for item in items[:max_results]:
            post_id = item.get("id", "")
            results.append({
                "post_id": f"IG-{post_id}",
                "platform": "Instagram",
                "author": "Anonymous (IG Privacy)", # Graph API Hashtag tidak mereturn username author demi privasi
                "handle": "@instagram_user",
                "created_at": item.get("timestamp", datetime.now().isoformat()),
                "content": item.get("caption", ""),
                "url": item.get("permalink", f"https://www.instagram.com/p/{post_id}/"),
                "likes": int(item.get("like_count", 0)),
                "comments": int(item.get("comments_count", 0))
            })
            
        return results

    except Exception as e:
        print(f"Error fetching Instagram API data: {e}")
        return []

if __name__ == "__main__":
    test_data = fetch_instagram_data("Edukasi", 2)
    print("Instagram Data:", test_data)
