import os
import asyncio
# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

async def _fetch_tweets_async(keyword: str, max_results: int) -> list[dict]:
    # twscrape module is imported here to avoid issues if not installed
    # pyrefly: ignore [missing-import]
    from twscrape import API, gather
    
    api = API()
    
    # 1. Pastikan akun dummy ada di pool
    username = os.environ.get("TWITTER_USERNAME")
    password = os.environ.get("TWITTER_PASSWORD")
    email = os.environ.get("TWITTER_EMAIL")
    email_password = os.environ.get("TWITTER_EMAIL_PASSWORD")
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    
    if not username or not password:
        print("Kredensial akun Twitter dummy tidak lengkap di .env. Menghentikan scraping X.")
        return []
    
    # Periksa apakah kita punya cookies
    cookies_str = None
    if auth_token and ct0:
        cookies_str = f"auth_token={auth_token}; ct0={ct0};"

    # Periksa apakah akun sudah ada di database pool
    try:
        await api.pool.add_account(username, password, email, email_password, cookies=cookies_str)
        await api.pool.login_all()
    except Exception as e:
        print(f"Peringatan saat inisialisasi akun twscrape: {e}")
        # Tetap lanjut, mungkin akun sudah ada dan login
        
    # 2. Ambil tweets menggunakan fungsi search
    tweets = []
    try:
        # q (query) = keyword
        # gather takes an async generator and returns a list
        raw_tweets = await gather(api.search(keyword, limit=max_results))
        
        for t in raw_tweets:
            tweets.append({
                "post_id": f"X-{t.id}",
                "platform": "X/Twitter",
                "author": t.user.displayname,
                "handle": f"@{t.user.username}",
                "created_at": t.date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": t.rawContent,
                "url": t.url,
                "likes": t.likeCount,
                "shares": t.retweetCount, # shares map to retweets
                "comments": t.replyCount
            })
            
    except Exception as e:
        print(f"Error fetching X (Twitter) data: {e}")
        
    return tweets

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_twitter_data(keyword: str, max_results: int = 20) -> list[dict]:
    """
    Fungsi wrapper sinkron (synchronous) untuk memanggil kode async twscrape dari Streamlit.
    """
    # pyrefly: ignore [missing-import]
    import nest_asyncio
    # pyrefly: ignore [missing-import]
    nest_asyncio.apply()
    try:
        # Menjalankan event loop asyncio secara independen
        return asyncio.run(_fetch_tweets_async(keyword, max_results))
    except Exception as e:
        print(f"Gagal menjalankan async task Twitter: {e}")
        return []

if __name__ == "__main__":
    # Test lokal
    print("Testing X (Twitter) Scraper...")
    res = fetch_twitter_data("Edukasi", max_results=3)
    print(f"Berhasil menarik {len(res)} tweets!")
    if res:
        print(res[0])
