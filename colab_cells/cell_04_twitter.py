# ============================================================
# CELL 4: SCRAPING TWITTER (SELENIUM UNDETECTED)
# ============================================================
import time
import urllib.parse
from datetime import datetime
import os

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    pass

# Simpan driver di level global agar login hanya 1x sepanjang program jalan
TWITTER_DRIVER = None

def scrape_twitter(keyword, max_results=100):
    global TWITTER_DRIVER
    
    print(f"    - Twitter Selenium: mencari '{keyword}'...")
    
    if TWITTER_DRIVER is None:
        print("    [!] Membuka Chrome untuk Twitter pertama kali...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--lang=id')
        options.add_argument('--disable-features=Translate')
        # Gunakan version_main=153 sesuai Chrome laptop Anda
        TWITTER_DRIVER = uc.Chrome(options=options, version_main=153)
        
        TWITTER_DRIVER.get("https://x.com/login")
        print("\n" + "="*60)
        print("🚨 TINDAKAN DIBUTUHKAN (TWITTER) 🚨")
        print("1. Jendela Chrome sudah terbuka.")
        print("2. Silakan LOGIN X/Twitter dan lewati Captcha secara MANUAL.")
        print("3. JANGAN tekan Enter sebelum Anda masuk ke Beranda X!")
        print("="*60 + "\n")
        
        input("👉 TEKAN ENTER DI SINI JIKA SUDAH SELESAI LOGIN & CAPTCHA... ")
        print("    [OK] Melanjutkan ke pencarian...")
        
        time.sleep(2)

    # 2. Mulai Pencarian
    # Tambahkan lang:id agar hasil pencarian dipaksa berbahasa Indonesia
    search_keyword = keyword if "lang:" in keyword else f"{keyword} lang:id"
    query = urllib.parse.quote(search_keyword)
    url = f"https://x.com/search?q={query}&src=typed_query&f=live"
    
    TWITTER_DRIVER.get(url)
    
    # Tunggu tweet pertama muncul
    try:
        WebDriverWait(TWITTER_DRIVER, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
        )
    except Exception:
        pass
        
    time.sleep(3)
    
    results = []
    last_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
    seen_urls = set()
    
    extract_js = """
    const posts = [];
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    
    for (const article of articles) {
        let content = "";
        const textDiv = article.querySelector('div[data-testid="tweetText"]');
        if (textDiv) content = textDiv.innerText.trim();
        
        // Bersihkan spasi berlebih tapi pertahankan newline/enter
        content = content.replace(/\\s*\\n\\s*/g, '\\n').trim();
        
        let author = "";
        let handle = "";
        const userDiv = article.querySelector('div[data-testid="User-Name"]');
        if (userDiv) {
            const spans = userDiv.querySelectorAll('span');
            for (const span of spans) {
                if (span.innerText.startsWith('@')) {
                    handle = span.innerText;
                } else if (!author && span.innerText.trim() && !span.innerText.startsWith('@')) {
                    author = span.innerText;
                }
            }
        }
        
        let likes = 0, retweets = 0, comments = 0, views = 0;
        const group = article.querySelector('div[role="group"]');
        if (group) {
            const label = group.getAttribute('aria-label') || "";
            const parts = label.toLowerCase().split(',');
            for (const p of parts) {
                const numMatch = p.match(/\\d+/g);
                if (!numMatch) continue;
                const num = parseInt(numMatch.join(''));
                
                if (p.includes('suka') || p.includes('like')) likes = num;
                else if (p.includes('balas') || p.includes('repl')) comments = num;
                else if (p.includes('posting ulang') || p.includes('repost') || p.includes('retweet')) retweets = num;
                else if (p.includes('tayangan') || p.includes('view')) views = num;
            }
        }
        
        let url = "";
        let date = "";
        const timeEl = article.querySelector('time');
        if (timeEl) {
            date = timeEl.getAttribute('datetime') || "";
            const a = timeEl.closest('a');
            if (a) url = a.href;
        }
        
        if (content && url) {
            posts.push({
                content: content,
                author: author || "Unknown",
                handle: handle,
                likes: likes,
                retweets: retweets,
                comments: comments,
                views: views,
                url: url,
                date: date
            });
        }
    }
    return posts;
    """
    
    while len(results) < max_results:
        try:
            # Klik tombol Show More jika ada untuk semua tweet di layar
            TWITTER_DRIVER.execute_script("""
                document.querySelectorAll('div[data-testid="tweet-text-show-more-link"]').forEach(btn => btn.click());
            """)
            time.sleep(1.5) # Tunggu agar Twitter sempat memuat sisa teks
            
            extracted = TWITTER_DRIVER.execute_script(extract_js)
            for post in extracted:
                if len(results) >= max_results:
                    break
                    
                url_tweet = post.get('url', '')
                if not url_tweet or url_tweet in seen_urls:
                    continue
                    
                content = post.get('content', '')
                if not content:
                    continue
                    
                seen_urls.add(url_tweet)
                
                results.append({
                    "post_id": f"twitter_{abs(hash(url_tweet)) % 1000000}",
                    "platform": "Twitter",
                    "author": post.get('author', ''),
                    "handle": post.get('handle', ''),
                    "content": content,
                    "description": "",
                    "created_at": post.get('date', '') or datetime.now().isoformat(),
                    "likes": post.get('likes', 0),
                    "shares": post.get('retweets', 0), # Menggunakan retweets di kolom shares
                    "comments": post.get('comments', 0),
                    "views": post.get('views', 0),
                    "url": url_tweet,
                    "keyword": keyword,
                    "scraped_at": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"    [WARN] JS Extract error: {e}")
                
        if len(results) >= max_results:
            break
            
        TWITTER_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(2)
            new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    return results

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Twitter (Selenium)...")
    data = scrape_twitter("makan bergizi gratis", max_results=5)
    print(f"Berhasil ambil {len(data)} data")
    if TWITTER_DRIVER:
        TWITTER_DRIVER.quit()

