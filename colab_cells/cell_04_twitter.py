# ============================================================
# CELL 4: SCRAPING TWITTER/X (SELENIUM UNDETECTED)
# - 2 Fase: Kumpulkan URL → Ekstraksi di Tab Baru
# - Filter tanggal: 1 Januari 2025 - sekarang
# - Deduplikasi URL global
# - Auto-resume support
# - Tanpa batasan max_results (full crawl)
# ============================================================
import time
import urllib.parse
import os
import subprocess
import random
from datetime import datetime, timezone, timedelta

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

# Path untuk Chrome profile persisten (login disimpan)
TW_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".tw_scraper_profile")

# WIB timezone (UTC+7)
WIB = timezone(timedelta(hours=7))

# Tanggal cutoff: 1 Januari 2025
DATE_CUTOFF = datetime(2025, 1, 1, tzinfo=timezone.utc)

# ---- Global tracking ----
_SEEN_URLS = set()  # URL tweet yang sudah pernah di-scrape


def reset_tracking():
    """Reset tracking (untuk awal run baru tanpa resume)."""
    global _SEEN_URLS
    _SEEN_URLS = set()


def load_seen_urls(urls):
    """Load URL yang sudah ada dari CSV sebelumnya (untuk resume)."""
    global _SEEN_URLS
    _SEEN_URLS.update(urls)
    print(f"    [DEDUP] {len(_SEEN_URLS)} URL sudah diketahui, akan di-skip.")


# ---- Helpers ----

def _to_wib(date_str):
    """Convert ISO datetime string ke format WIB."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        dt_wib = dt.astimezone(WIB)
        return dt_wib.strftime('%Y-%m-%d %H:%M:%S') + ' WIB'
    except Exception:
        return date_str


def _is_after_cutoff(date_str):
    """Cek apakah tanggal tweet >= 1 Januari 2025."""
    if not date_str:
        return True  # Jika tidak ada tanggal, tetap ambil
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt >= DATE_CUTOFF
    except Exception:
        return True


def _init_driver():
    """Buat driver baru dengan profile persisten."""
    global TWITTER_DRIVER

    # Tutup driver lama jika ada
    if TWITTER_DRIVER is not None:
        try:
            TWITTER_DRIVER.quit()
        except:
            pass
        TWITTER_DRIVER = None

    # Kill semua proses chrome yang menggantung
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, timeout=5)
        time.sleep(2)
    except:
        pass

    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--lang=id-ID,id,en-US,en')
    options.add_argument('--disable-features=Translate')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument(f'--user-data-dir={TW_PROFILE_DIR}')

    # Set preferensi bahasa bawaan Chrome ke Bahasa Indonesia
    prefs = {
        "intl.accept_languages": "id-ID,id,en-US,en",
        "translate": {"enabled": False} # Matikan popup otomatis Google Translate
    }
    options.add_experimental_option("prefs", prefs)

    # Fix infinite hang when downloading chromedriver
    import socket
    socket.setdefaulttimeout(30)

    try:
        TWITTER_DRIVER = uc.Chrome(options=options, version_main=154)
    except Exception as e:
        print(f"    [WARN] Gagal init uc.Chrome dengan version_main=154, mencoba tanpa: {e}")
        TWITTER_DRIVER = uc.Chrome(options=options)

    # Cek apakah sudah login
    TWITTER_DRIVER.get("https://x.com/home")
    print("    [INFO] Menunggu beranda Twitter dimuat...")
    time.sleep(5)
    
    print("\n" + "=" * 60)
    print("🚨 WAJIB CEK BROWSER TWITTER (X) 🚨")
    print("1. Jendela Chrome sudah terbuka di layar Anda.")
    print("2. Pastikan Anda SUDAH LOGIN dan melihat feed/beranda normal.")
    print("3. Jika disuruh Login / Captcha / Verifikasi Email, kerjakan DULU.")
    print("4. JANGAN lanjut jika layar browser masih error 'Something went wrong'.")
    print("=" * 60 + "\n")

    input("👉 TEKAN ENTER DI SINI HANYA JIKA BROWSER SUDAH LOGIN & AMAN... ")
    print("    [OK] Melanjutkan ke pencarian...")
    time.sleep(2)

    return TWITTER_DRIVER


def scrape_twitter(keyword, max_results=500):
    """
    Scrape Twitter/X dengan 2 fase:
    - Fase 1: Scroll halaman search untuk kumpulkan URL tweet
    - Fase 2: Buka setiap URL di tab baru untuk ekstraksi data detail
    
    Filter: hanya tweet dari 1 Januari 2025 - sekarang.
    """
    global TWITTER_DRIVER, _SEEN_URLS

    print(f"    - Twitter Selenium: mencari '{keyword}'...")

    if TWITTER_DRIVER is None:
        print("    [!] Membuka Chrome untuk Twitter pertama kali...")
        _init_driver()

    # ========== FASE 1: KUMPULKAN URL DARI SEARCH ==========
    print(f"    [FASE 1] Mengumpulkan URL tweet dari pencarian...")

    # Gunakan query biasa tanpa filter since atau lang, karena kita fokus ke Top engagement murni
    query_text = keyword
    query = urllib.parse.quote(query_text)
    
    # HAPUS parameter &f=live agar Twitter masuk ke tab "Top" (berdasarkan engagement/popularitas)
    url = f"https://x.com/search?q={query}&src=typed_query"

    TWITTER_DRIVER.get(url)

    # Tunggu tweet pertama muncul atau handle error
    try:
        WebDriverWait(TWITTER_DRIVER, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
        )
    except Exception:
        # Cek apakah terkena error "Something went wrong" atau "No results"
        try:
            body_text = (TWITTER_DRIVER.execute_script("return document.body.innerText") or "").lower()
            
            if "no results for" in body_text or "tidak ada hasil untuk" in body_text:
                print(f"    [INFO] Pencarian kosong (Tidak ada hasil). Melewati keyword ini.")
                return []
                
            error_keywords = ["something went wrong", "ada yang salah", "try reloading", "kesalahan teknis", "muat ulang", "rate limit", "batas frekuensi", "batas terlampaui", "cannot retrieve", "tidak dapat memuat"]
            if any(err in body_text for err in error_keywords):
                print("\n    [!] ERROR: Twitter memblokir pencarian (Sesi expired/terkena limit).")
                print("    [INFO] Memaksa logout untuk membersihkan sesi...")
                TWITTER_DRIVER.delete_all_cookies()
                TWITTER_DRIVER.get("https://x.com/login")
                time.sleep(3)
                
                print("\n" + "=" * 60)
                print("🚨 SESI TWITTER KEDALUWARSA / LIMIT 🚨")
                print("1. Jendela Chrome saat ini berada di halaman Login.")
                print("2. Silakan LOGIN ULANG (disarankan pakai AKUN TWITTER LAIN jika yang tadi terkena limit).")
                print("3. Setelah berhasil login, cobalah lakukan pencarian manual.")
                print("4. Jika pencarian manual berhasil, kembali ke sini dan tekan ENTER.")
                print("=" * 60 + "\n")
                
                input("👉 TEKAN ENTER JIKA SUDAH LOGIN ULANG & AMAN... ")
                
                # Coba muat ulang halaman pencariannya
                print("    [INFO] Melanjutkan pencarian...")
                TWITTER_DRIVER.get(url)
                WebDriverWait(TWITTER_DRIVER, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
        except Exception:
            pass

    time.sleep(3)
    
    # Cek jumlah tweet di layar untuk debug
    try:
        article_count = TWITTER_DRIVER.execute_script('return document.querySelectorAll(\'article[data-testid="tweet"]\').length')
        print(f"    [DEBUG] Jumlah tweet di layar awal: {article_count}")
        
        # Jika masih 0, cek dulu apakah benar-benar kosong
        if article_count == 0:
            body_text = (TWITTER_DRIVER.execute_script("return document.body.innerText") or "").lower()
            if "no results for" in body_text or "tidak ada hasil untuk" in body_text:
                print(f"    [INFO] Pencarian kosong (Tidak ada hasil). Melewati keyword ini.")
                return []
                
            print("    [!] Masih 0 tweet. Coba refresh paksa...")
            TWITTER_DRIVER.refresh()
            time.sleep(7)
            article_count = TWITTER_DRIVER.execute_script('return document.querySelectorAll(\'article[data-testid="tweet"]\').length')
            print(f"    [DEBUG] Jumlah tweet setelah refresh paksa: {article_count}")

            # Jika masih 0, coba cari tombol Retry
            if article_count == 0:
                clicked_retry = TWITTER_DRIVER.execute_script("""
                    let btns = document.querySelectorAll('button');
                    for (let btn of btns) {
                        let txt = (btn.innerText || '').toLowerCase();
                        if (txt.includes('retry') || txt.includes('coba lagi')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                """)
                if clicked_retry:
                    print("    [INFO] Menekan tombol 'Retry / Coba lagi' di layar awal...")
                    time.sleep(6)
                    article_count = TWITTER_DRIVER.execute_script('return document.querySelectorAll(\'article[data-testid="tweet"]\').length')
                    print(f"    [DEBUG] Jumlah tweet setelah Retry: {article_count}")

            # Jika setelah refresh & retry masih 0 tweet dan bukan karena 'no results':
            if article_count == 0:
                body_text = (TWITTER_DRIVER.execute_script("return document.body.innerText") or "").lower()
                if "no results for" in body_text or "tidak ada hasil untuk" in body_text:
                    print(f"    [INFO] Pencarian kosong (Tidak ada hasil). Melewati keyword ini.")
                    return []
                
                print("\n" + "=" * 60)
                print("🚨 TWITTER TIDAK MENAMPILKAN TWEET (RATE LIMIT / SESI MACET) 🚨")
                print(f"Keyword: '{keyword}' tidak memuat data di layar browser.")
                print("1. Cek jendela Chrome: apakah halaman blank, terkena limit pencarian, atau perlu re-login.")
                print("2. Jika akun terkena limit, Anda bisa ganti/login akun lain di browser Chrome tersebut.")
                print("3. Pastikan pencarian manual di Chrome berhasil memunculkan tweet.")
                print("4. Setelah aman, kembali ke sini dan tekan ENTER untuk mencoba lagi.")
                print("=" * 60 + "\n")
                input("👉 TEKAN ENTER JIKA SUDAH AMAN / SIAP COBA LAGI... ")
                TWITTER_DRIVER.get(url)
                time.sleep(5)
                article_count = TWITTER_DRIVER.execute_script('return document.querySelectorAll(\'article[data-testid="tweet"]\').length')
                print(f"    [DEBUG] Jumlah tweet setelah re-login/refresh: {article_count}")
    except:
        pass

    # Kumpulkan Data tweet dari halaman search secara LANGSUNG (Single-Phase)
    all_tweet_data = {} # dictionary url -> data
    last_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
    no_new_count = 0
    max_no_new = 8
    
    collect_data_js = r"""
    const results = [];
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    for (const article of articles) {
        try {
            let tweetUrl = '';
            const links = article.querySelectorAll('a[href*="/status/"]');
            for (const link of links) {
                if (link.href.includes('/status/') && !link.href.includes('/photo/') && !link.href.includes('/video/') && !link.href.includes('/analytics')) {
                    tweetUrl = link.href.split('?')[0];
                    break;
                }
            }
            if (!tweetUrl) continue;

            let dateStr = '';
            const timeEl = article.querySelector('time');
            if (timeEl) dateStr = timeEl.getAttribute('datetime') || '';

            let text = '';
            const textDiv = article.querySelector('div[data-testid="tweetText"]');
            if (textDiv) text = textDiv.innerText;

            let handle = '';
            const userLinks = article.querySelectorAll('a[role="link"]');
            for (const ul of userLinks) {
                const textContent = ul.innerText;
                if (textContent.includes('@')) {
                    const match = textContent.match(/@[\w_]+/);
                    if (match) {
                        handle = match[0];
                        break;
                    }
                }
            }

            let likes=0, views=0, retweets=0, replies=0;
            const groups = article.querySelectorAll('[role="group"]');
            if (groups.length > 0) {
                const btns = groups[0].querySelectorAll('[role="button"], a');
                for (const btn of btns) {
                    const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const testId = (btn.getAttribute('data-testid') || '').toLowerCase();
                    let valStr = btn.innerText.trim();
                    
                    let val = 0;
                    if (valStr) {
                        valStr = valStr.replace(/,/g, '');
                        if (valStr.match(/K/i)) val = parseFloat(valStr) * 1000;
                        else if (valStr.match(/M/i)) val = parseFloat(valStr) * 1000000;
                        else val = parseInt(valStr) || 0;
                    }

                    if (testId === 'reply' || aria.includes('balas') || aria.includes('reply')) replies = val;
                    else if (testId === 'retweet' || aria.includes('repost') || aria.includes('retweet')) retweets = val;
                    else if (testId === 'like' || aria.includes('suka') || aria.includes('like')) likes = val;
                    else if (aria.includes('tayangan') || aria.includes('view') || testId.includes('view')) views = val;
                }
            }

            results.push({
                url: tweetUrl,
                date: dateStr,
                text: text,
                username: handle,
                likes: likes,
                views: views,
                retweets: retweets,
                replies: replies
            });
        } catch(e) {}
    }
    return results;
    """

    while len(all_tweet_data) < max_results:
        try:
            extracted_data = TWITTER_DRIVER.execute_script(collect_data_js)
            count_before = len(all_tweet_data)

            for item in (extracted_data or []):
                tweet_url = item.get('url', '')
                if not tweet_url or tweet_url in all_tweet_data or tweet_url in _SEEN_URLS:
                    continue
                all_tweet_data[tweet_url] = item

            new_count = len(all_tweet_data) - count_before
            if new_count > 0:
                print(f"      [Scroll] {len(all_tweet_data)} Data terkumpul (+{new_count} baru)")

            if new_count == 0:
                clicked_retry = TWITTER_DRIVER.execute_script("""
                    let btns = document.querySelectorAll('div[data-testid="primaryColumn"] button');
                    for (let btn of btns) {
                        let txt = btn.innerText.toLowerCase();
                        if (txt.includes('retry') || txt.includes('coba lagi')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if clicked_retry:
                    print("      [INFO] Jaringan Twitter melambat. Menekan tombol 'Retry / Coba lagi'...")
                    time.sleep(5)
                    continue

                no_new_count += 1
                if no_new_count >= max_no_new:
                    if len(all_tweet_data) < max_results and "&f=live" not in url and max_results >= 1000:
                        print(f"    [INFO] Tab 'Top' habis ({len(all_tweet_data)} data). Beralih otomatis ke tab 'Latest' untuk melengkapi {max_results}...")
                        url = url + "&f=live"
                        TWITTER_DRIVER.get(url)
                        no_new_count = 0
                        time.sleep(5)
                        continue
                    else:
                        print(f"    [INFO] Mentok maksimal! {max_no_new}x scroll tanpa data baru. Berhenti.")
                        break
            else:
                no_new_count = 0

            if len(all_tweet_data) >= max_results:
                break

            TWITTER_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.0, 4.0))

            body_text = (TWITTER_DRIVER.execute_script("return document.body.innerText") or "").lower()
            error_keywords = ["something went wrong", "ada yang salah", "try reloading", "kesalahan teknis", "muat ulang", "rate limit", "batas frekuensi", "batas terlampaui", "cannot retrieve", "tidak dapat memuat"]
            if any(err in body_text for err in error_keywords):
                print("\n    [!] ERROR DI TENGAH SCROLL: Twitter memblokir pencarian.")
                print("    [INFO] Memaksa logout...")
                TWITTER_DRIVER.delete_all_cookies()
                TWITTER_DRIVER.get("https://x.com/login")
                time.sleep(3)
                
                print("\n" + "=" * 60)
                print("🚨 SESI TWITTER KEDALUWARSA / LIMIT DI TENGAH JALAN 🚨")
                print("1. Silakan LOGIN ULANG (pakai AKUN TWITTER LAIN jika limit).")
                print("2. Jika pencarian manual berhasil, kembali ke sini dan tekan ENTER.")
                print("=" * 60 + "\n")
                
                input("👉 TEKAN ENTER JIKA SUDAH LOGIN ULANG & AMAN... ")
                
                print("    [INFO] Melanjutkan pencarian (scroll ulang dari atas)...")
                TWITTER_DRIVER.get(url)
                time.sleep(5)
                continue

            new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(2)
                new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_new_count += 1
            last_height = new_height

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"    [WARN] Error saat scroll: {e}")
            break

    print(f"    [INFO] Selesai. Total {len(all_tweet_data)} data tweet berhasil diekstrak.")
    
    # Format hasil akhir
    final_data = []
    for item in all_tweet_data.values():
        date_str = item['date']
        clean_text = item['text'].replace('\n', ' ').replace('\r', ' ')
        
        final_data.append({
            'platform': 'Twitter',
            'keyword': keyword,
            'url': item['url'],
            'handle': item['username'],
            'content': clean_text,
            'created_at': _to_wib(date_str),
            'likes': item['likes'],
            'comments': item['replies'],
            'reposts': item['retweets'],
            'views': item['views'],
            'scraped_at': datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S') + ' WIB',
        })
        _SEEN_URLS.add(item['url'])

    return final_data


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Twitter (Selenium - 2 Fase)...")
    reset_tracking()
    data = scrape_twitter("makan bergizi gratis", max_results=10)
    print(f"Berhasil ambil {len(data)} data")
    for d in data:
        print(f" -> {d['handle']} | Likes: {d['likes']} | {d['created_at']} | Content: {str(d['content'])[:50]}...")
    if TWITTER_DRIVER:
        TWITTER_DRIVER.quit()
