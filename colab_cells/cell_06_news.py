from cell_02_config import *
# ============================================================
# CELL 6: SCRAPER GOOGLE NEWS
# Tools: feedparser (Ringan, Cepat, Bebas Rate-Limit)
# Target: ~100 artikel per keyword
# ============================================================

from datetime import datetime
import time
import re
import urllib.parse
import feedparser

def _extract_article_text(url):
    """Coba ambil teks lengkap artikel menggunakan newspaper3k."""
    try:
        from newspaper import Article
        article = Article(url, language='id')
        article.download()
        article.parse()
        return article.text[:2000] if article.text else ""
    except:
        return ""


def scrape_news(keyword, max_results=100):
    """
    Scrape Google News menggunakan RSS Feed.
    Ini persis seperti fungsi yang berjalan di dashboard lokal (web local),
    lebih cepat, ringan, dan tidak terkena rate limit seperti GNews.
    Ditambah full-text extraction untuk konten yang lebih kaya.
    """
    results = []
    seen_urls = set()

    try:
        query = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
        
        feed = feedparser.parse(rss_url)
        
        for idx, entry in enumerate(feed.entries):
            if len(results) >= max_results:
                break
                
            url = entry.get("link", "")
            title = entry.get("title", "")
            
            if url in seen_urls or not title:
                continue
            seen_urls.add(url)
            
            # Ambil nama publisher dari title (format: "Judul - Publisher")
            pub_name = getattr(entry, "source", {}).get("title", "")
            if not pub_name and " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                pub_name = parts[1].strip() if len(parts) > 1 else "Berita Online"
            elif not pub_name:
                pub_name = "Berita Online"
                
            published = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            summary = entry.get("summary", "")
            # Bersihkan HTML dari summary
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            
            # Coba ambil full-text artikel (hanya 10 artikel pertama per keyword
            # agar tidak terlalu lama)
            full_text = ""
            if idx < 10:
                full_text = _extract_article_text(url)
            
            results.append({
                "post_id": f"news_rss_{idx}_{abs(hash(url)) % 1000000}",
                "platform": "News",
                "author": pub_name,
                "handle": "",
                "content": title,
                "description": summary[:300] if summary else "",
                "full_text": full_text,
                "created_at": published,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "views": 0,
                "url": url,
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f"    [!] News RSS feed error: {str(e)[:80]}")

    return results

# ============================================================
# TEST
# ============================================================
print("[TEST] Menguji Google News scraper (RSS/Web Local version)...")
test = scrape_news("Makan Bergizi Gratis", max_results=10)
print(f"[OK] News: {len(test)} artikel ditemukan")
for t in test[:3]:
    print(f"   [ARTIKEL] {t['content'][:70]}...")
    print(f"      Publisher: {t['author']} | Tanggal: {t['created_at'][:30]}")

