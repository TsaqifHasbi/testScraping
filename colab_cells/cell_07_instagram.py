# ============================================================
# CELL 7: SCRAPING INSTAGRAM (SELENIUM UNDETECTED)
# ============================================================
import time
import urllib.parse
from bs4 import BeautifulSoup
import os
from datetime import datetime

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    pass

IG_DRIVER = None

def scrape_instagram(keyword, max_results=50):
    global IG_DRIVER
    
    print(f"    - Instagram Selenium: mencari '{keyword}'...")
    
    if IG_DRIVER is None:
        print("    [!] Membuka Chrome untuk Instagram pertama kali...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--disable-notifications")
        
        IG_DRIVER = uc.Chrome(options=options, version_main=153)
        
        IG_DRIVER.get("https://www.instagram.com/accounts/login/")
        print("\n" + "="*60)
        print("🚨 TINDAKAN DIBUTUHKAN (INSTAGRAM) 🚨")
        print("1. Jendela Chrome sudah terbuka.")
        print("2. Silakan LOGIN dan SELESAIKAN CAPTCHA/2FA secara MANUAL.")
        print("3. JANGAN tekan Enter sebelum Anda masuk ke Beranda IG!")
        print("="*60 + "\n")
        
        input("👉 TEKAN ENTER DI SINI JIKA SUDAH SELESAI LOGIN & CAPTCHA... ")
        print("    [OK] Melanjutkan ke pencarian...")
        
        time.sleep(2)

    # 2. Mulai Pencarian Hashtag
    # Hapus spasi untuk pencarian hashtag, misal "Makan Bergizi Gratis" jadi "makanbergizigratis"
    hashtag = keyword.replace(" ", "").lower()
    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
    
    IG_DRIVER.get(url)
    time.sleep(5)
    
    results = []
    last_height = IG_DRIVER.execute_script("return document.body.scrollHeight")
    
    while len(results) < max_results:
        soup = BeautifulSoup(IG_DRIVER.page_source, 'html.parser')
        
        # IG post links di halaman explore
        links = soup.find_all('a', href=True)
        
        for link in links:
            if len(results) >= max_results:
                break
                
            href = link['href']
            if '/p/' in href or '/reel/' in href:
                url_post = "https://www.instagram.com" + href
                
                # Coba ambil alt text image sebagai content (biasanya berisi caption potong)
                img = link.find('img')
                content = img['alt'] if img and img.has_attr('alt') else f"Post Instagram #{hashtag}"
                
                if not any(r['url'] == url_post for r in results):
                    results.append({
                        "post_id": f"ig_{abs(hash(url_post)) % 1000000}",
                        "platform": "Instagram",
                        "author": "Instagram User",
                        "handle": "",
                        "content": content[:500] + "..." if len(content) > 500 else content,
                        "description": "",
                        "created_at": datetime.now().isoformat(),
                        "likes": 0,
                        "shares": 0,
                        "comments": 0,
                        "views": 0,
                        "url": url_post,
                        "keyword": keyword,
                        "scraped_at": datetime.now().isoformat(),
                        "topic": "UNKNOWN"
                    })
                    
        if len(results) >= max_results:
            break
            
        IG_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        
        new_height = IG_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            new_height = IG_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    return results

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Instagram (Selenium)...")
    data = scrape_instagram("makan bergizi gratis", max_results=10)
    print(f"Berhasil ambil {len(data)} data")
    if IG_DRIVER:
        IG_DRIVER.quit()
