# ============================================================
# CELL 7: SCRAPING INSTAGRAM (SELENIUM UNDETECTED)
# - Multi-hashtag per keyword untuk volume lebih banyak
# - Deduplikasi URL global (tidak scrape post yang sama 2x)
# - Konversi waktu ke WIB
# - Tracking hashtag yang sudah dikunjungi
# ============================================================
import time
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
    # pyrefly: ignore [missing-import]
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    pass

IG_DRIVER = None

# Path untuk Chrome profile persisten (login disimpan)
IG_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".ig_scraper_profile")

# WIB timezone (UTC+7)
WIB = timezone(timedelta(hours=7))

# ---- Global tracking ----
_VISITED_HASHTAGS = set()   # Hashtag yang sudah pernah dibuka
_SEEN_URLS = set()          # URL post yang sudah pernah di-scrape


def reset_tracking():
    """Reset tracking (untuk awal run baru tanpa resume)."""
    global _VISITED_HASHTAGS, _SEEN_URLS
    _VISITED_HASHTAGS = set()
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


def _keyword_to_hashtags(keyword):
    """
    Convert keyword riset ke daftar hashtag Instagram yang relevan.
    Contoh: 'keracunan MBG' -> ['keracunanmbg', 'mbg', 'makanbergizigratis']
    Skip hashtag yang sudah pernah dikunjungi dalam sesi ini.
    """
    global _VISITED_HASHTAGS

    kw_lower = keyword.lower().strip()
    full_tag = kw_lower.replace(" ", "").replace("#", "")

    candidates = [full_tag]

    # Hanya gunakan 1 hashtag persis dari keyword tanpa tambahan fallback
    # sesuai permintaan user agar data tidak melenceng.
    
    # Deduplikasi & filter yang sudah dikunjungi
    seen = set()
    result = []
    for tag in candidates:
        if tag and tag not in seen and tag not in _VISITED_HASHTAGS:
            seen.add(tag)
            result.append(tag)

    return result


def _init_driver():
    """Buat driver baru dengan profile persisten."""
    global IG_DRIVER
    # Tutup driver lama jika ada
    if IG_DRIVER is not None:
        try:
            IG_DRIVER.quit()
        except:
            pass
        IG_DRIVER = None

    # Kill semua proses chrome yang menggantung
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, timeout=5)
        time.sleep(2)
    except:
        pass

    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument(f'--user-data-dir={IG_PROFILE_DIR}')

    # Fix infinite hang when downloading chromedriver by setting a global timeout
    import socket
    socket.setdefaulttimeout(30)

    try:
        IG_DRIVER = uc.Chrome(options=options, version_main=154)
    except Exception as e:
        print(f"    [WARN] Gagal init uc.Chrome dengan version_main=154, mencoba tanpa argumen: {e}")
        IG_DRIVER = uc.Chrome(options=options)

    # Cek apakah sudah login (profile persisten)
    IG_DRIVER.get("https://www.instagram.com/")
    time.sleep(4)
    # Cek apakah sudah login berdasarkan keberadaan cookie 'sessionid'
    cookies = IG_DRIVER.get_cookies()
    is_logged_in = any(c.get('name') == 'sessionid' for c in cookies)

    current_url = IG_DRIVER.current_url
    if not is_logged_in or "/challenge" in current_url:
        print("\n" + "="*60)
        print("🚨 TINDAKAN DIBUTUHKAN (INSTAGRAM) 🚨")
        print("1. Jendela Chrome sudah terbuka.")
        print("2. Silakan LOGIN dan SELESAIKAN CAPTCHA/2FA secara MANUAL.")
        print("3. JANGAN tekan Enter sebelum Anda masuk ke Beranda IG!")
        print("4. Setelah login, sesi akan TERSIMPAN (tidak perlu login lagi).")
        print("="*60 + "\n")

        input("👉 TEKAN ENTER DI SINI JIKA SUDAH SELESAI LOGIN & CAPTCHA... ")
        print("    [OK] Melanjutkan ke pencarian...")
        time.sleep(2)
    else:
        print("    [OK] Sesi login tersimpan! Otomatis masuk tanpa login ulang.")

    return IG_DRIVER


def _search_urls_via_google(keyword, max_urls=200):
    """
    Cari URL Instagram via Google site search.
    Menemukan postingan yang menyebut keyword di CAPTION, bukan cuma hashtag.
    Google mengindex Instagram jauh lebih baik dari DuckDuckGo.
    """
    global _SEEN_URLS
    # pyrefly: ignore [missing-import]
    from googlesearch import search

    found_urls = []
    found_set = set()

    # Variasi query untuk hasil lebih banyak
    queries = [
        f'site:instagram.com/p/ "{keyword}"',
        f'site:instagram.com/reel/ "{keyword}"',
        f'site:instagram.com "{keyword}" instagram',
    ]

    for query in queries:
        if len(found_urls) >= max_urls:
            break

        print(f"      [GOOGLE] Mencari: {query}")
        try:
            results = search(query, num_results=min(100, max_urls - len(found_urls)), lang="id")
            for link in results:
                # Filter hanya URL post/reel Instagram
                if ('instagram.com/p/' in link or 'instagram.com/reel/' in link):
                    clean_url = link.split('?')[0]
                    if not clean_url.endswith('/'):
                        clean_url += '/'
                    if clean_url not in found_set and clean_url not in _SEEN_URLS:
                        found_urls.append(clean_url)
                        found_set.add(clean_url)

            print(f"      [GOOGLE] +{len(found_urls)} URL ditemukan sejauh ini")
        except Exception as e:
            print(f"      [GOOGLE WARN] Error pada query '{query}': {e}")

        # Jeda antar query agar tidak diblokir Google
        time.sleep(random.uniform(3.0, 6.0))

    print(f"      [GOOGLE] Total {len(found_urls)} URL unik dari Google")
    return found_urls


def scrape_instagram(keyword, max_results=50, use_google=False, use_hashtag=True):
    global IG_DRIVER, _VISITED_HASHTAGS, _SEEN_URLS

    print(f"    - Instagram Selenium: mencari '{keyword}'...")

    if IG_DRIVER is None:
        print("    [!] Membuka Chrome untuk Instagram pertama kali...")
        _init_driver()

    # ========== FASE 1: KUMPULKAN URL ==========
    MIN_URLS = max_results
    all_post_urls = []
    all_urls_set = set()
    hashtag_url_counts = {}

    # --- Metode 1: Google Site Search (keyword di caption) ---
    if use_google:
        print("    [FASE 1A] Pencarian keyword via Google site:instagram.com ...")
        google_urls = _search_urls_via_google(keyword, max_urls=max_results)
        for url in google_urls:
            if url not in all_urls_set and url not in _SEEN_URLS:
                all_post_urls.append(url)
                all_urls_set.add(url)
        print(f"    [GOOGLE] {len(all_post_urls)} URL baru dari keyword search")

    # --- Metode 2: Hashtag Search (jika masih kurang) ---
    if use_hashtag and len(all_post_urls) < MIN_URLS:
        print(f"    [FASE 1B] Hashtag search (masih butuh {MIN_URLS - len(all_post_urls)} URL lagi)...")

        hashtags = _keyword_to_hashtags(keyword)
        if hashtags:
            print(f"    - Hashtags: {['#' + h for h in hashtags]}")

            def _scroll_hashtag_page(hashtag, target_count):
                """Scroll halaman hashtag dan kumpulkan URL. Return jumlah URL baru."""
                nonlocal all_post_urls, all_urls_set

                tag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                print(f"      [Hashtag] Membuka #{hashtag} (target: {target_count} URL)...")

                try:
                    IG_DRIVER.get(tag_url)
                    time.sleep(3)

                    body_text = IG_DRIVER.execute_script(
                        "return (document.body && document.body.innerText) || ''"
                    ) or ""
                    body_lower = body_text.lower()
                    if ("tidak tersedia" in body_lower
                            or "isn't available" in body_lower
                            or "sorry, this page" in body_lower
                            or "no results" in body_lower
                            or "we couldn't find anything" in body_lower
                            or "belum ada postingan" in body_lower
                            or "no posts yet" in body_lower):
                        print(f"      [!] #{hashtag} tidak ditemukan (No Results). Skip.")
                        return 0

                    scroll_attempts = 0
                    max_scroll = 15
                    prev_total = len(all_post_urls)

                    while (len(all_post_urls) - prev_total) < target_count:
                        post_elements = IG_DRIVER.find_elements(
                            By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']"
                        )
                        count_before = len(all_post_urls)

                        for el in post_elements:
                            try:
                                href = el.get_attribute('href')
                                if (href
                                        and '/c/' not in href
                                        and href not in _SEEN_URLS
                                        and href not in all_urls_set):
                                    all_post_urls.append(href)
                                    all_urls_set.add(href)
                            except:
                                pass

                        new_from_this = len(all_post_urls) - prev_total
                        total_now = len(all_post_urls)
                        print(f"      - #{hashtag}: +{new_from_this} URL (total keseluruhan: {total_now}/{MIN_URLS})...")

                        if new_from_this >= target_count:
                            break

                        if len(all_post_urls) == count_before:
                            scroll_attempts += 1
                            if scroll_attempts >= max_scroll:
                                print(f"      [!] #{hashtag}: Mentok setelah {max_scroll}x scroll tanpa URL baru.")
                                break
                        else:
                            scroll_attempts = 0

                        try:
                            IG_DRIVER.execute_script("window.scrollBy(0, 3000);")
                        except:
                            pass
                        time.sleep(random.uniform(2.0, 3.5))

                    new_total = len(all_post_urls) - prev_total
                    print(f"      [Hashtag] #{hashtag}: {new_total} URL baru dikumpulkan.")
                    return new_total

                except Exception as e:
                    print(f"      [WARN] Error pada #{hashtag}: {e}")
                    return 0

            for hashtag in hashtags:
                _VISITED_HASHTAGS.add(hashtag)
                remaining = MIN_URLS - len(all_post_urls)
                if remaining <= 0:
                    break
                target = max(remaining, 40)
                count = _scroll_hashtag_page(hashtag, target)
                hashtag_url_counts[hashtag] = count

                if len(all_post_urls) >= MIN_URLS:
                    print(f"    [✓] Sudah mencapai {len(all_post_urls)} URL (>= {MIN_URLS}). Lanjut ke Fase 2.")
                    break
        else:
            print(f"    [SKIP] Semua hashtag untuk '{keyword}' sudah pernah dikunjungi.")

    # Limit ke max_results
    all_post_urls = all_post_urls[:max_results]
    print(f"    [INFO] Fase 1 Selesai. Total {len(all_post_urls)} URL unik (DDG + Hashtag).")

    if not all_post_urls:
        return []

    # ========== FASE 2: EKSTRAKSI DATA DI TAB BARU ==========
    print("    [INFO] Fase 2: Mulai ekstraksi data di Tab Baru...")
    results = []
    main_window = IG_DRIVER.current_window_handle
    consecutive_failures = 0

    for idx, url_post in enumerate(all_post_urls):
        print(f"      [{idx+1}/{len(all_post_urls)}] Ekstraksi: {url_post}")

        # Stop jika 5x berturut-turut gagal (kemungkinan diblokir)
        if consecutive_failures >= 5:
            print("      [!] 5x berturut-turut gagal. Kemungkinan diblokir. Berhenti untuk keyword ini.")
            break

        try:
            # 1. Buka tab baru
            IG_DRIVER.execute_script(f"window.open('{url_post}', '_blank');")
            time.sleep(1)

            # 2. Pindah ke Tab Baru
            if len(IG_DRIVER.window_handles) > 1:
                IG_DRIVER.switch_to.window(IG_DRIVER.window_handles[-1])
            else:
                print("      [WARN] Tab baru gagal terbuka. Skip.")
                continue

            # 3. Tunggu halaman loading
            try:
                WebDriverWait(IG_DRIVER, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except:
                pass

            # Jeda agar React SPA selesai render (dibuat lebih cepat)
            time.sleep(random.uniform(1.0, 3.0))

            # 4. Debug info
            page_title = IG_DRIVER.title or ""
            page_url = IG_DRIVER.current_url or ""
            body_text = IG_DRIVER.execute_script(
                "return (document.body && document.body.innerText) || ''"
            ) or ""
            body_preview = body_text[:300].replace('\n', ' | ')

            print(f"        [DEBUG] Title: {page_title[:80]}")
            print(f"        [DEBUG] URL: {page_url}")
            print(f"        [DEBUG] Body (300 char): {body_preview[:150]}...")

            # Cek error page
            body_lower = body_text.lower()
            if "error 429" in body_lower or "too many requests" in body_lower:
                print("      [!!!] HTTP ERROR 429 Terdeteksi! Meminta pergantian akun...")
                try:
                    IG_DRIVER.delete_all_cookies()
                    IG_DRIVER.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
                except:
                    pass
                IG_DRIVER.get("https://www.instagram.com/accounts/login/")
                print("      =====================================================")
                print("      [ACTION REQUIRED] Silakan login dengan AKUN BARU di Chrome yang terbuka.")
                input("      [ACTION REQUIRED] Tekan ENTER di terminal ini jika sudah berhasil masuk ke feed...")
                print("      =====================================================")
                consecutive_failures += 1
                IG_DRIVER.close()
                IG_DRIVER.switch_to.window(main_window)
                
                # Coba refresh halaman utama agar ikut menggunakan sesi baru
                try:
                    IG_DRIVER.refresh()
                    time.sleep(5)
                except:
                    pass

                if consecutive_failures >= 3:
                     print("      [!!!] Rate Limit membandel. Lanjut ke hashtag/keyword berikutnya.")
                     return results
                continue
            elif "isn't working" in body_lower or "tidak tersedia" in body_lower or "page not found" in body_lower or "can’t be reached" in body_lower or "can't be reached" in body_lower or "err_quic" in body_lower or "err_timed_out" in body_lower:
                print("      [!] Halaman error/tidak tersedia. Skip.")
                consecutive_failures += 1
                IG_DRIVER.close()
                IG_DRIVER.switch_to.window(main_window)
                time.sleep(random.uniform(0.5, 1.5))
                continue

            # Cek redirect ke login
            if "/accounts/login" in page_url or "/challenge/" in page_url:
                print("      [!] Halaman redirect ke login/challenge. Skip.")
                consecutive_failures += 1
                IG_DRIVER.close()
                IG_DRIVER.switch_to.window(main_window)
                time.sleep(random.uniform(0.5, 1.5))
                continue

            # 5. Ekstrak data — JavaScript AGRESIF dengan banyak fallback
            js_extract = """
            return (function() {
                let data = {
                    handle: '',
                    content: '',
                    date: '',
                    likes: 0,
                    comments: 0,
                    views: 0,
                    is_video: false,
                    debug_selectors: {}
                };
                
                // ===== HANDLE (Username) =====
                let handleSelectors = [
                    'header a[href*="/"] span',
                    'header a[role="link"]',
                    'header a',
                    'h2 a',
                    'a[href*="/"] > span > span',
                    'article a[href*="/"]'
                ];
                for (let sel of handleSelectors) {
                    let el = document.querySelector(sel);
                    if (el) {
                        let txt = el.innerText.trim();
                        if (txt && txt.length < 40 && !txt.includes(' ') && !txt.includes('\\n')) {
                            data.handle = txt;
                            data.debug_selectors.handle = sel;
                            break;
                        }
                    }
                }
                
                // Fallback: dari og:url
                if (!data.handle) {
                    let ogUrl = document.querySelector('meta[property="og:url"]');
                    if (ogUrl) {
                        let match = ogUrl.content.match(/instagram\\.com\\/([^/]+)/);
                        if (match && match[1] !== 'p' && match[1] !== 'reel') {
                            data.handle = match[1];
                            data.debug_selectors.handle = 'og:url';
                        }
                    }
                }
                
                // Fallback: dari title "Username on Instagram: ..."
                if (!data.handle) {
                    let title = document.title || '';
                    let titleMatch = title.match(/^(.+?)\\s+on Instagram/i) || title.match(/^(.+?)\\s+di Instagram/i) || title.match(/^(.+?)\\s*\\(@/);
                    if (titleMatch) {
                        data.handle = titleMatch[1].trim();
                        data.debug_selectors.handle = 'title';
                    }
                }
                
                // ===== CONTENT (Caption) =====
                let h1El = document.querySelector('h1');
                if (h1El && h1El.innerText.trim().length > 5) {
                    data.content = h1El.innerText.trim();
                    data.debug_selectors.content = 'h1';
                }
                
                if (!data.content) {
                    let metaDesc = document.querySelector('meta[name="description"]');
                    if (metaDesc) {
                        let desc = metaDesc.getAttribute('content') || '';
                        let colonIdx = desc.indexOf(': ');
                        if (colonIdx > -1 && colonIdx < desc.length - 5) {
                            data.content = desc.substring(colonIdx + 2).replace(/"/g, '');
                            data.debug_selectors.content = 'meta:description';
                        } else {
                            let dashIdx = desc.indexOf(' - ');
                            if (dashIdx > -1 && dashIdx < desc.length - 5) {
                                data.content = desc.substring(dashIdx + 3);
                                data.debug_selectors.content = 'meta:description-dash';
                            }
                        }
                    }
                }
                
                if (!data.content) {
                    let ogDesc = document.querySelector('meta[property="og:description"]');
                    if (ogDesc) {
                        data.content = ogDesc.getAttribute('content') || '';
                        data.debug_selectors.content = 'og:description';
                    }
                }
                
                if (!data.content) {
                    let spans = Array.from(document.querySelectorAll('span'));
                    let caption = spans.find(s => s.innerText.length > 30 && !s.innerText.includes('Log in') && !s.innerText.includes('likes'));
                    if (caption) {
                        data.content = caption.innerText;
                        data.debug_selectors.content = 'span-fallback';
                    }
                }
                
                // ===== DATE =====
                let timeEl = document.querySelector('time[datetime]');
                if (timeEl) {
                    data.date = timeEl.getAttribute('datetime');
                    data.debug_selectors.date = 'time';
                }
                
                // ===== LIKES & COMMENTS dari Meta =====
                let metaDesc2 = document.querySelector('meta[name="description"]');
                if (metaDesc2) {
                    let descText = metaDesc2.getAttribute('content') || '';
                    let likeMatch = descText.match(/([\\d,.\\u00a0]+)\\s*(likes|suka|Likes)/);
                    if (likeMatch) data.likes = parseInt(likeMatch[1].replace(/[,.\\u00a0]/g, ''));
                    
                    let commentMatch = descText.match(/([\\d,.\\u00a0]+)\\s*(comments|komentar|Comments)/);
                    if (commentMatch) data.comments = parseInt(commentMatch[1].replace(/[,.\\u00a0]/g, ''));
                    
                    // ===== VIEWS (Reels/Video) dari Meta =====
                    let viewMatch = descText.match(/([\\d,.\\u00a0]+)\\s*(plays|views|tayangan|kali diputar|Plays|Views)/);
                    if (viewMatch) {
                        data.views = parseInt(viewMatch[1].replace(/[,.\\u00a0]/g, ''));
                        data.debug_selectors.views = 'meta:description';
                    }
                }
                
                // ===== LIKES fallback dari section =====
                if (data.likes === 0) {
                    let sectionSpans = Array.from(document.querySelectorAll('section span, section a span, button span'));
                    for (let s of sectionSpans) {
                        let t = s.innerText.toLowerCase();
                        if (t.includes('suka') || t.includes('like')) {
                            let num = parseInt(t.replace(/[^0-9]/g, ''));
                            if (!isNaN(num) && num > 0) {
                                data.likes = num;
                                break;
                            }
                        }
                    }
                }
                
                // ===== VIEWS fallback dari DOM (Reels menampilkan "X views/plays") =====
                if (data.views === 0) {
                    let allSpans = Array.from(document.querySelectorAll('span'));
                    for (let s of allSpans) {
                        let t = s.innerText.toLowerCase().trim();
                        if (t.match(/^[\\d,.]+\\s*(plays|views|tayangan|kali diputar)$/)) {
                            let num = parseInt(t.replace(/[^0-9]/g, ''));
                            if (!isNaN(num) && num > 0) {
                                data.views = num;
                                data.debug_selectors.views = 'span-fallback';
                                break;
                            }
                        }
                    }
                }
                
                // ===== VIDEO / REEL DETECTION =====
                if (document.querySelector('video')) {
                    data.is_video = true;
                }

                return data;
            })();
            """

            extracted = IG_DRIVER.execute_script(js_extract)

            # Debug print
            debug_sel = extracted.get('debug_selectors', {})
            print(f"        [DEBUG] Selectors used: {debug_sel}")
            print(f"        [DEBUG] handle='{extracted.get('handle')}' | likes={extracted.get('likes')} | views={extracted.get('views')} | date={extracted.get('date')}")

            # Terima data meskipun handle kosong, asalkan ada content atau likes
            has_useful_data = extracted.get('handle') or extracted.get('content') or extracted.get('likes', 0) > 0

            if not has_useful_data:
                print("      [WARN] Data benar-benar kosong. Skip.")
                consecutive_failures += 1
            else:
                consecutive_failures = 0  # Reset karena berhasil

                handle = extracted.get('handle', '') or 'instagram_user'

                # Convert date ke WIB
                created_at = _to_wib(extracted.get('date', ''))
                if not created_at:
                    created_at = datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S') + ' WIB'

                # Deteksi jenis postingan dari DOM (ada tag video) atau URL
                is_vid = extracted.get('is_video', False)
                post_type = "Reel" if is_vid or "/reel/" in url_post or "/video/" in url_post else "Photo"

                results.append({
                    "post_id": f"ig_{abs(hash(url_post)) % 1000000}",
                    "platform": "Instagram",
                    "post_type": post_type,
                    "author": handle,
                    "handle": f"@{handle}",
                    "content": str(extracted.get('content', '')).replace('\n', ' | ').replace('\r', '').replace('\u2028', ' ').replace('\u2029', ' '),
                    "description": "",
                    "created_at": created_at,
                    "likes": extracted.get('likes', 0),
                    "comments": extracted.get('comments', 0),
                    "url": url_post,
                    "keyword": keyword,
                    "scraped_at": datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S') + ' WIB',
                    "topic": "UNKNOWN"
                })

                # Mark URL as seen
                _SEEN_URLS.add(url_post)

                print(f"        [OK] Data berhasil! @{handle} | {post_type} | Likes: {extracted.get('likes', 0)}")
                extracted_data_count = len(results)

            # 6. Tutup tab dan kembali ke halaman utama
            IG_DRIVER.close()
            IG_DRIVER.switch_to.window(main_window)

            # JEDA ACAK SETELAH MENUTUP TAB
            time.sleep(random.uniform(1.0, 2.0))

            # Istirahat setiap 30 post berhasil
            if len(results) > 0 and len(results) % 30 == 0:
                pause_time = random.uniform(5, 10)  # dipercepat jadi 5-10 detik
                print(f"      [PAUSE] Istirahat {int(pause_time)} detik setelah {len(results)} post (anti rate-limit)...")
                time.sleep(pause_time)

        except Exception as e:
            print(f"      [WARN] Gagal ekstrak {url_post}: {e}")
            consecutive_failures += 1
            try:
                # Pastikan kembali ke tab utama
                if len(IG_DRIVER.window_handles) > 1:
                    IG_DRIVER.close()
                IG_DRIVER.switch_to.window(main_window)
                time.sleep(2)
            except:
                pass
            continue

    print(f"    [INFO] Fase 2 Selesai. Total {len(results)} data berhasil diekstrak dari {len(all_post_urls)} URL.")
    return results


# ============================================================
# TEST
# ============================================================
# FUNGSI SCRAPING MENGGUNAKAN GRAMSCRAPER API
# ============================================================
import requests
import json
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

def scrape_instagram_api(keyword, max_results=50):
    """
    Scrape Instagram via GramScraper API.
    Keyword diubah menjadi hashtag (spasi dihilangkan).
    """
    global _SEEN_URLS
    
    load_dotenv()
    api_key = os.getenv("GRAMSCRAPER_API_KEY")
    
    if not api_key:
        print("    [!] ERROR: GRAMSCRAPER_API_KEY tidak ditemukan di .env!")
        return []
        
    hashtag = keyword.lower().replace(" ", "").replace("#", "")
    print(f"    - GramScraper API: mencari hashtag '#{hashtag}' (Target: {max_results} data)...")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    results = []
    seen_in_this_run = set()
    next_page_id = None
    
    while len(results) < max_results:
        url = f"https://gramscraper.com/api/instagram/v2/hashtag/medias/recent?name={hashtag}"
        if next_page_id:
            url += f"&max_id={next_page_id}"
            
        try:
            print(f"      [API] Fetching dari GramScraper (Data terkumpul: {len(results)})...")
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                print(f"      [API] Request gagal: {res.status_code}")
                print(res.text)
                break
                
            data = res.json()
            
            items = data.get('response', [])
            if not isinstance(items, dict) or 'sections' not in items:
                print("      [API] Format response tidak sesuai harapan atau tidak ada data.")
                break
                
            new_posts = 0
            for section in items['sections']:
                layout = section.get('layout_content', {})
                medias = layout.get('medias', [])
                for m in medias:
                    if 'media' not in m:
                        continue
                        
                    p = m['media']
                    post_id = p.get('id')
                    code = p.get('code')
                    
                    if not code:
                        continue
                        
                    url_post = f"https://www.instagram.com/p/{code}/"
                    
                    if url_post in _SEEN_URLS or url_post in seen_in_this_run:
                        continue
                        
                    seen_in_this_run.add(url_post)
                    _SEEN_URLS.add(url_post)
                    
                    # Ekstrak data sesuai format CSV kita
                    user = p.get('user', {})
                    username = user.get('username', '')
                    fullname = user.get('full_name', '')
                    
                    caption_text = ""
                    caption_obj = p.get('caption')
                    if caption_obj and isinstance(caption_obj, dict):
                        caption_text = caption_obj.get('text', '')
                        
                    # Tanggal
                    taken_at = p.get('taken_at')
                    if taken_at:
                        # taken_at biasanya unix timestamp
                        dt = datetime.fromtimestamp(taken_at, tz=WIB)
                        created_at = dt.strftime('%Y-%m-%d %H:%M:%S') + ' WIB'
                    else:
                        created_at = ""
                        
                    is_video = p.get('media_type') == 2 or p.get('media_type') == 8
                    post_type = 'Reel/Video' if is_video else 'Photo'
                    
                    post_data = {
                        'post_id': f"ig_{post_id}" if post_id else f"ig_{code}",
                        'platform': 'Instagram',
                        'post_type': post_type,
                        'author': fullname if fullname else username,
                        'handle': f"@{username}",
                        'content': caption_text.replace('\n', ' | '),
                        'description': '',
                        'created_at': created_at,
                        'likes': p.get('like_count', 0),
                        'comments': p.get('comment_count', 0),
                        'url': url_post,
                        'keyword': keyword,
                        'scraped_at': datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S WIB')
                    }
                    
                    results.append(post_data)
                    new_posts += 1
                    
                    if len(results) >= max_results:
                        break
                
                if len(results) >= max_results:
                    break
                    
            print(f"      [API] +{new_posts} post baru ditemukan.")
            
            # Cek paginasi
            if not data.get('next_page_id'):
                print("      [API] Tidak ada halaman selanjutnya (mentok).")
                break
                
            next_page_id = data.get('next_page_id')
            
            # Rate limiting API
            time.sleep(1)
            
        except Exception as e:
            print(f"      [API ERROR] {e}")
            break
            
    print(f"    [OK] Selesai scraping '{keyword}'. Total didapat: {len(results)}")
    return results

# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Instagram (Selenium)...")
    reset_tracking()
    data = scrape_instagram("makan bergizi gratis", max_results=5)
    print(f"Berhasil ambil {len(data)} data")
    for d in data:
        print(f" -> {d['handle']} | Likes: {d['likes']} | {d['created_at']} | Content: {str(d['content'])[:50]}...")
    if IG_DRIVER:
        IG_DRIVER.quit()
