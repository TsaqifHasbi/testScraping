import os
import streamlit as st
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load env variables
load_dotenv()

@st.cache_data(show_spinner=False, ttl=3601)
def fetch_youtube_data(keyword: str, max_results: int = 20) -> list[dict]:
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY not found in environment variables.")
        return []

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        # 1. Search for videos
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            maxResults=max_results,
            order="relevance",
            regionCode="ID"
        )
        response = request.execute()
        
        items = response.get("items", [])
        if not items:
            return []
            
        # 2. Get statistics for those videos
        video_ids = [item["id"]["videoId"] for item in items]
        stats_request = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        )
        stats_response = stats_request.execute()
        
        stats_map = {}
        for stat_item in stats_response.get("items", []):
            stats_map[stat_item["id"]] = stat_item.get("statistics", {})
        
        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            stats = stats_map.get(video_id, {})
            
            pub_date = snippet.get("publishedAt", "")
            pub_date_clean = pub_date.replace("T", " ")[:16] if pub_date else ""
            
            results.append({
                "post_id": f"YT-{video_id}",
                "platform": "YouTube",
                "author": snippet.get("channelTitle", "Unknown"),
                "handle": f"@{snippet.get('channelTitle', 'Unknown').replace(' ', '')}",
                "created_at": pub_date_clean,
                "content": f"{snippet.get('title', '')}\n{snippet.get('description', '')}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "likes": int(stats.get("likeCount", 0)),
                "views": int(stats.get("viewCount", 0)),
                "comments": int(stats.get("commentCount", 0))
            })
            
        return results
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return []
