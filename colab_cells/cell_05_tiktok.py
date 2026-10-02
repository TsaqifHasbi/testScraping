# ============================================================
# CELL 5: SCRAPING TIKTOK (SELENIUM UNDETECTED)
# ============================================================
import time
import urllib.parse
from bs4 import BeautifulSoup
import json
import re

def parse_eng(text):
    if not text: return '0'
    text = text.lower().replace(' ', '')
    m = re.search(r'([\d\.,]+)([kmrbjtribuja]*)', text)
    if not m: return '0'
    
    num_str = m.group(1).replace(',', '.')
    try:
        num = float(num_str)
    except:
        return '0'
        
    suffix = m.group(2)
    if 'k' in suffix or 'rb' in suffix or 'ribu' in suffix:
        num *= 1000
    elif 'm' in suffix or 'jt' in suffix or 'juta' in suffix:
        num *= 1000000
        
    return str(int(num))

import os

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    pass

TIKTOK_DRIVER = None

def scrape_tiktok(keyword, max_results=100):
    global TIKTOK_DRIVER
    
    def traverse_tiktok_json(obj, stats_dict, caps_dict):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, dict):
                    if 'stats' in v and isinstance(v['stats'], dict) and 'diggCount' in v['stats']:
                        vid = str(v.get('id', k))
                        st = v['stats']
                        stats_dict[vid] = {
                            'likes': str(st.get('diggCount', '0')),
                            'comments': str(st.get('commentCount', '0')),
                            'shares': str(st.get('shareCount', '0')),
                            'views': str(st.get('playCount', '0'))
                        }
                        if v.get('desc'):
                            caps_dict[vid] = re.sub(r'[\r\n\u2028\u2029]+', ' ', str(v['desc'])).strip()
                    traverse_tiktok_json(v, stats_dict, caps_dict)
                elif isinstance(v, list):
                    traverse_tiktok_json(v, stats_dict, caps_dict)
        elif isinstance(obj, list):
            for item in obj:
                traverse_tiktok_json(item, stats_dict, caps_dict)
    
    print(f"    - TikTok Selenium: mencari '{keyword}'...")
    
    if TIKTOK_DRIVER is None:
        print("    [!] Membuka Chrome untuk TikTok pertama kali...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        # Gunakan version_main=153
        TIKTOK_DRIVER = uc.Chrome(options=options, version_main=153)
        print("    [INFO] Halaman TikTok akan terbuka. Jika ada CAPTCHA (puzzle), selesaikan manual!")
        TIKTOK_DRIVER.get("https://www.tiktok.com/")
        input("    [ACTION REQUIRED] Tekan ENTER di sini JIKA halamannya sudah berhasil dimuat dan terbebas dari CAPTCHA...")

    query = urllib.parse.quote(keyword)
    url = f"https://www.tiktok.com/search?q={query}"
    
    try:
        TIKTOK_DRIVER.get(url)
    except Exception as e:
        print(f"    [ERROR] Gagal membuka URL: {e}")
        return []
    
    # Tunggu beberapa detik agar halaman ter-load
    time.sleep(5)
    
    results = []
    last_height = TIKTOK_DRIVER.execute_script("return document.body.scrollHeight")
    
    while len(results) < max_results:
        html_source = TIKTOK_DRIVER.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Pre-extract JSON stats for all videos on the search page!
        page_stats = {}
        page_caps = {}
        sigi = re.search(r'window\[\'SIGI_STATE\'\]=(.*?);window\[', html_source)
        rehyd = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html_source, re.DOTALL)
        try:
            if sigi:
                traverse_tiktok_json(json.loads(sigi.group(1)), page_stats, page_caps)
            elif rehyd:
                traverse_tiktok_json(json.loads(rehyd.group(1)), page_stats, page_caps)
        except Exception as e:
            print(f"      [!] Gagal memparse JSON di halaman pencarian: {e}")
            
        video_cards = soup.find_all('div', {'class': lambda x: x and 'DivItemContainer' in x})
        if not video_cards:
            video_cards = soup.find_all('div', {'data-e2e': 'search_top-item'})
            
        for card in video_cards:
            if len(results) >= max_results:
                break
                
            try:
                link_tag = card.find('a', href=True)
                url_video = link_tag['href'] if link_tag else "Unknown"
                
                if "video" not in url_video:
                    continue
                    
                author_tag = card.find('p', {'data-e2e': 'search-card-user-unique-id'})
                author = author_tag.text.strip() if author_tag else "TikTok_User"
                
                views_tag = card.find('strong', {'data-e2e': 'video-views'})
                if not views_tag:
                    views_tag = card.find('div', {'data-e2e': 'video-views'})
                views = parse_eng(views_tag.text.strip()) if views_tag else "0"
                
                caption_tag = card.find('div', {'data-e2e': 'search-card-video-caption'})
                caption = caption_tag.text.strip() if caption_tag else f"Video TikTok dari {author}"
                
                if url_video != "Unknown" and not any(r['url'] == url_video for r in results):
                    vid_id_match = re.search(r'/video/(\d+)', url_video)
                    vid_id = vid_id_match.group(1) if vid_id_match else ""
                    
                    likes = "0"
                    comments = "0"
                    shares = "0"
                    
                    if vid_id and vid_id in page_stats:
                        likes = page_stats[vid_id].get('likes', '0')
                        comments = page_stats[vid_id].get('comments', '0')
                        shares = page_stats[vid_id].get('shares', '0')
                        if page_stats[vid_id].get('views', '0') != '0':
                            views = page_stats[vid_id].get('views', '0')
                    
                    if vid_id and vid_id in page_caps:
                        caption = page_caps[vid_id]
                    
                    # Jika JSON tidak mendeteksi (misalnya karena lazy-load) atau caption terpotong
                    # Buka modal video untuk mendapatkan caption full dan data riil!
                    # Buka modal video untuk mendapatkan caption full dan data riil!
                    # Buka tab baru untuk setiap video agar mendapat data 100% utuh
                    try:
                        # Buka video di tab baru
                        TIKTOK_DRIVER.execute_script(f"window.open('{url_video}', '_blank');")
                        
                        # Pindah ke tab baru (tab terakhir)
                        TIKTOK_DRIVER.switch_to.window(TIKTOK_DRIVER.window_handles[-1])
                        time.sleep(3) # Tunggu halaman video dimuat
                        
                        video_html = TIKTOK_DRIVER.page_source
                        video_soup = BeautifulSoup(video_html, 'html.parser')
                        
                        # Coba ambil json dari halaman video (sangat akurat)
                        vid_sigi = re.search(r'window\[\'SIGI_STATE\'\]=(.*?);window\[', video_html)
                        vid_rehyd = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', video_html, re.DOTALL)
                        
                        if vid_sigi or vid_rehyd:
                            try:
                                json_data = json.loads(vid_sigi.group(1)) if vid_sigi else json.loads(vid_rehyd.group(1))
                                
                                v_item = {}
                                if 'ItemModule' in json_data and vid_id in json_data['ItemModule']:
                                    v_item = json_data['ItemModule'][vid_id]
                                elif '__DEFAULT_SCOPE__' in json_data:
                                    try:
                                        v_item = json_data['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
                                    except KeyError:
                                        pass
                                
                                if v_item:
                                    if 'stats' in v_item:
                                        if str(v_item['stats'].get('diggCount', '0')) != '0': likes = str(v_item['stats'].get('diggCount', '0'))
                                        if str(v_item['stats'].get('commentCount', '0')) != '0': comments = str(v_item['stats'].get('commentCount', '0'))
                                        if str(v_item['stats'].get('shareCount', '0')) != '0': shares = str(v_item['stats'].get('shareCount', '0'))
                                        if str(v_item['stats'].get('playCount', '0')) != '0': views = str(v_item['stats'].get('playCount', '0'))
                                    if v_item.get('desc'):
                                        caption = re.sub(r'[\r\n\u2028\u2029]+', ' ', str(v_item['desc'])).strip()
                            except:
                                pass
                        
                        # Fallback ke DOM parsing
                        like_tag = video_soup.find(attrs={'data-e2e': 'like-count'}) or video_soup.find(attrs={'data-e2e': 'browse-like-count'}) or video_soup.find('strong', {'data-e2e': 'like-count'})
                        comment_tag = video_soup.find(attrs={'data-e2e': 'comment-count'}) or video_soup.find(attrs={'data-e2e': 'browse-comment-count'})
                        share_tag = video_soup.find(attrs={'data-e2e': 'share-count'}) or video_soup.find(attrs={'data-e2e': 'browse-share-count'})
                        
                        # H1 di halaman video biasanya adalah deskripsi
                        desc_tag = video_soup.find(attrs={'data-e2e': 'browse-video-desc'}) or video_soup.find('h1', {'data-e2e': 'video-desc'})
                        if not desc_tag:
                            # Fallback cari h1 di dalam container
                            container = video_soup.find('div', class_=lambda x: x and 'DivVideoInfoContainer' in x)
                            if container:
                                desc_tag = container.find('h1')
                        
                        if like_tag and like_tag.text: likes = parse_eng(like_tag.text.strip())
                        if comment_tag and comment_tag.text: comments = parse_eng(comment_tag.text.strip())
                        if share_tag and share_tag.text: shares = parse_eng(share_tag.text.strip())
                        if desc_tag and desc_tag.text: caption = re.sub(r'[\r\n\u2028\u2029]+', ' ', desc_tag.get_text(separator=" ")).strip()
                        
                        # Pastikan views juga ikut ketarik dari halaman video
                        views_tag = video_soup.find(attrs={'data-e2e': 'play-count'}) or video_soup.find(attrs={'data-e2e': 'browse-play-count'})
                        if views_tag and views_tag.text: views = parse_eng(views_tag.text.strip())
                            
                        # Tutup tab ini
                        TIKTOK_DRIVER.close()
                        # Kembali ke tab pencarian
                        TIKTOK_DRIVER.switch_to.window(TIKTOK_DRIVER.window_handles[0])
                    except Exception as e:
                        # Pastikan selalu kembali ke tab 0 meskipun error
                        try:
                            if len(TIKTOK_DRIVER.window_handles) > 1:
                                TIKTOK_DRIVER.close()
                                TIKTOK_DRIVER.switch_to.window(TIKTOK_DRIVER.window_handles[0])
                        except:
                            pass
                    
                    results.append({
                        "platform": "TikTok",
                        "topic": "UNKNOWN",
                        "content": caption,
                        "author": author,
                        "url": url_video,
                        "views": views,
                        "likes": likes, 
                        "comments": comments,
                        "shares": shares
                    })
                    print(f"  -> Video {author} | V: {views} | L: {likes} | C: {comments} | S: {shares}")
                    
            except Exception:
                pass

        if len(results) >= max_results:
            break
            
        TIKTOK_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        
        new_height = TIKTOK_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(2)
            new_height = TIKTOK_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    return results

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape TikTok (Selenium)...")
    data = scrape_tiktok("makan bergizi gratis", max_results=10)
    print(f"Berhasil ambil {len(data)} data")
    if TIKTOK_DRIVER:
        TIKTOK_DRIVER.quit()
