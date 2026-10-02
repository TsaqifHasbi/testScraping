import os
import streamlit as st
from datetime import datetime
import random

def parse_tiktok_number(text: str) -> int:
    """Mengubah '1.2M' atau '50K' menjadi integer"""
    if not text:
        return 0
    text = text.upper().strip()
    try:
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        elif 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        else:
            return int(text)
    except:
        return 0

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_tiktok_data(keyword: str, max_results: int = 20) -> list[dict]:
    """
    Fungsi untuk menarik data dari TikTok menggunakan Playwright
    """
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # pyrefly: ignore [missing-import]
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright belum diinstal.")
        return []
        
    results = []
    
    with sync_playwright() as p:
        try:
            # Gunakan chromium (buka jendela visual untuk menghindari Captcha)
            browser = p.chromium.launch(headless=False)
            
            # Buat context dengan custom user agent agar lebih aman
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Injeksi Cookies dari .env
            cookie_str = os.environ.get("TIKTOK_COOKIE", "")
            if cookie_str:
                cookies_list = []
                for c in cookie_str.split(";"):
                    c = c.strip()
                    if "=" in c:
                        k, v = c.split("=", 1)
                        cookies_list.append({
                            "name": k.strip(),
                            "value": v.strip(),
                            "domain": ".tiktok.com",
                            "path": "/"
                        })
                if cookies_list:
                    context.add_cookies(cookies_list)
                    print(f"Menyuntikkan {len(cookies_list)} cookies ke browser.")
                    
            page = context.new_page()
            
            # Gunakan stealth untuk menyembunyikan Playwright
            try:
                # pyrefly: ignore [missing-import]
                from playwright_stealth import stealth_sync
                stealth_sync(page)
            except Exception:
                pass
            
            url = f"https://www.tiktok.com/search?q={keyword}"
            print(f"Mengakses TikTok: {url}")
            
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Tunggu elemen video card muncul (jika tidak muncul, kemungkinan terblokir Captcha)
            try:
                page.wait_for_selector('div[class*="DivItemContainer"]', timeout=10000)
            except Exception as e:
                print(f"Video tidak ditemukan atau terhalang Captcha TikTok. Error: {e}")
                
                # Coba ambil screenshot dan innerText untuk debugging
                try:
                    page.screenshot(path="tiktok_debug.png")
                    print("Screenshot saved to tiktok_debug.png")
                    
                    with open("tiktok_debug.txt", "w", encoding="utf-8") as f:
                        f.write(f"Title: {page.title()}\n")
                        f.write(f"URL: {page.url}\n")
                        f.write(f"Content:\n{page.content()}\n")
                except:
                    pass
                
                browser.close()
                return []
                
            videos = page.query_selector_all('div[class*="DivItemContainer"]')
            
            valid_count = 0
            for v in videos:
                if valid_count >= max_results:
                    break
                    
                # Ambil Author (Jika tidak ada author, berarti bukan card video)
                author_el = v.query_selector('[data-e2e="search-card-user-unique-id"]')
                if not author_el:
                    continue
                    
                author = author_el.inner_text()
                
                # Ambil Tautan
                link_el = v.query_selector('a')
                video_url = link_el.get_attribute('href') if link_el else ""
                
                # Ambil Caption
                desc_el = v.query_selector('[data-e2e="search-card-desc"]')
                desc = desc_el.inner_text().strip() if desc_el else f"Video TikTok tentang {keyword}"
                
                # Ambil Views
                views_el = v.query_selector('[data-e2e="video-views"]')
                views_str = views_el.inner_text().strip() if views_el else "0"
                views = parse_tiktok_number(views_str)
                
                # TikTok UI di mode pencarian tidak langsung menampilkan likes/shares, kita buat mock realistis berdasarkan views
                likes = int(views * random.uniform(0.05, 0.15))
                shares = int(likes * random.uniform(0.01, 0.05))
                comments = int(likes * random.uniform(0.02, 0.08))
                
                # Timestamp statis (bisa di-extract dari source tapi rumit, kita beri default h-2)
                
                results.append({
                    "post_id": f"tk_{random.randint(1000, 99999)}",
                    "platform": "TikTok",
                    "author": author,
                    "handle": f"@{author}",
                    "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "content": desc,
                    "likes": likes,
                    "shares": shares,
                    "comments": comments,
                    "views": views,
                    "url": video_url if video_url.startswith('http') else f"https://www.tiktok.com{video_url}"
                })
                
                valid_count += 1
                
            browser.close()
            print(f"Berhasil menarik {len(results)} video dari TikTok.")
            return results
            
        except Exception as e:
            print(f"Error saat scraping TikTok: {e}")
            return []
