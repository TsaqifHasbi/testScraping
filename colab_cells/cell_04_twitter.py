# ============================================================
# CELL 4: SCRAPING TWITTER (SELENIUM UNDETECTED)
# ============================================================
import time
import urllib.parse
from datetime import datetime
import os

try:
    # pyrefly: ignore [missing-import]
    import undetected_chromedriver as uc
    # pyrefly: ignore [missing-import]
    from selenium.webdriver.common.by import By
    # pyrefly: ignore [missing-import]
    from selenium.webdriver.support.ui import WebDriverWait
    # pyrefly: ignore [missing-import]
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
    # Tambahkan lang:id agar hasil pencarian berbahasa Indonesia
    from datetime import datetime
    cutoff_date = datetime(2024, 1, 1)  # Sejak awal 2024
    # Gunakan keyword apa adanya tanpa lang:id (keyword sudah bahasa Indonesia)
    query = urllib.parse.quote(keyword)
    # TIDAK pakai lang:id karena membuat Twitter mengembalikan tweet sangat tua
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
    
    # === DEBUG: Cek kondisi halaman ===
    try:
        article_count = TWITTER_DRIVER.execute_script('return document.querySelectorAll(\'article[data-testid="tweet"]\').length')
        page_title = TWITTER_DRIVER.title
        current_url = TWITTER_DRIVER.current_url
        print(f"    [DEBUG] URL: {current_url[:80]}...")
        print(f"    [DEBUG] Title: {page_title}")
        print(f"    [DEBUG] Jumlah tweet di halaman: {article_count}")
        if article_count == 0:
            # Cek apakah ada pesan error/kosong
            body_text = TWITTER_DRIVER.execute_script('return document.body.innerText.substring(0, 300)')
            print(f"    [DEBUG] Body text: {body_text[:200]}")
    except Exception as e:
        print(f"    [DEBUG] Error saat cek halaman: {e}")
    
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
            // Metode 1: Parsing dari aria-label grup tombol
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
            
            // Metode 2: Fallback - ambil views dari link analytics (elemen terakhir di group)
            if (views === 0) {
                const analyticsLink = group.querySelector('a[href*="/analytics"]');
                if (analyticsLink) {
                    const vText = analyticsLink.getAttribute('aria-label') || analyticsLink.innerText || '';
                    const vMatch = vText.match(/([\\d,\\.]+)/g);
                    if (vMatch) {
                        views = parseInt(vMatch.join('').replace(/,/g, ''));
                    }
                }
            }
            
            // Metode 3: Fallback - ambil dari tombol-tombol individual via aria-label
            if (likes === 0 && comments === 0 && retweets === 0) {
                const buttons = group.querySelectorAll('button[data-testid]');
                for (const btn of buttons) {
                    const testId = btn.getAttribute('data-testid') || '';
                    const ariaL = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const numM = ariaL.match(/([\\d,]+)/);
                    if (!numM) continue;
                    const val = parseInt(numM[1].replace(/,/g, ''));
                    
                    if (testId === 'like' || ariaL.includes('like') || ariaL.includes('suka')) likes = val;
                    else if (testId === 'reply' || ariaL.includes('repl') || ariaL.includes('balas')) comments = val;
                    else if (testId === 'retweet' || ariaL.includes('repost') || ariaL.includes('retweet')) retweets = val;
                }
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
            print(f"    [DEBUG] JS returned: {len(extracted) if extracted else 0} posts")
            if extracted and len(extracted) > 0:
                print(f"    [DEBUG] Post pertama: url={extracted[0].get('url','N/A')[:50]}, content={str(extracted[0].get('content',''))[:50]}")
            for post in extracted:
                if len(results) >= max_results:
                    break
                    
                url_tweet = post.get('url', '')
                if not url_tweet or url_tweet in seen_urls:
                    continue
                    
                content = post.get('content', '')
                if not content:
                    continue
                
                # Filter tweet tua (lebih dari 6 bulan)
                tweet_date_str = post.get('date', '')
                if tweet_date_str:
                    try:
                        tweet_dt = datetime.fromisoformat(tweet_date_str.replace('Z', '+00:00'))
                        if tweet_dt.replace(tzinfo=None) < cutoff_date:
                            print(f"    [DEBUG] SKIP tweet tua: {tweet_date_str}")
                            continue  # Skip tweet terlalu tua
                    except:
                        pass
                    
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
                    "reposts": post.get('retweets', 0), # Mengganti nama shares menjadi reposts sesuai permintaan
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

