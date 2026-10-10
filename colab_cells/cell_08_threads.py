from cell_02_config import *
# ============================================================
# CELL 8: SCRAPER THREADS (SELENIUM UNDETECTED)
# ============================================================

import time
import urllib.parse
from datetime import datetime
import re

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

THREADS_DRIVER = None

def scrape_threads(keyword, max_results=30):
    global THREADS_DRIVER
    
    print(f"    - Threads Selenium: mencari '{keyword}'...")
    
    if THREADS_DRIVER is None:
        print("    [!] Membuka Chrome untuk Threads pertama kali...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--lang=id')
        options.add_argument('--disable-features=Translate')
        
        # Sesuaikan dengan versi Chrome
        THREADS_DRIVER = uc.Chrome(options=options, version_main=153)
        
        THREADS_DRIVER.get("https://www.threads.net/login")
        print("\n" + "="*60)
        print("[!] TINDAKAN DIBUTUHKAN (THREADS) [!]")
        print("1. Jendela Chrome sudah terbuka.")
        print("2. Silakan LOGIN akun Instagram/Threads secara MANUAL.")
        print("3. JANGAN tekan Enter sebelum Anda masuk ke Beranda Threads!")
        print("="*60 + "\n")
        
        input(">>> TEKAN ENTER DI SINI JIKA SUDAH SELESAI LOGIN... ")
        print("    [OK] Melanjutkan ke pencarian...")
        time.sleep(2)

    # Mulai Pencarian
    query = urllib.parse.quote(keyword)
    url = f"https://www.threads.net/search?q={query}&serp_type=default"
    
    THREADS_DRIVER.get(url)
    
    # Tunggu sebentar agar halaman dan JS-nya load
    time.sleep(5)
    
    results = []
    last_height = THREADS_DRIVER.execute_script("return document.body.scrollHeight")
    
    # JavaScript extractor yang lebih canggih
    extract_js = """
    const posts = [];
    const seen = new Set();
    
    // Cari container post menggunakan beberapa selector
    const selectors = [
        'div[data-pressable-container="true"]',
        'article',
        'div[role="article"]',
    ];
    
    let containers = [];
    for (const sel of selectors) {
        containers = document.querySelectorAll(sel);
        if (containers.length >= 2) break;
    }
    
    if (containers.length >= 2) {
        for (const container of containers) {
            const fullText = container.innerText.trim();
            if (!fullText || fullText.length < 20) continue;
            
            // === AUTHOR ===
            let author = '';
            const authorLink = container.querySelector('a[href*="/@"]');
            if (authorLink) {
                author = authorLink.innerText.trim().replace('@', '');
            }
            
            // === CONTENT (ambil semua span teks) ===
            const spans = container.querySelectorAll('span[dir="auto"]');
            let contentArr = [];
            for (const span of spans) {
                // Hindari duplikasi jika ada span di dalam span
                if (span.parentElement && span.parentElement.closest('span[dir="auto"]')) continue;
                
                const t = span.innerText.trim();
                if (!t) continue;
                
                // Abaikan teks author atau teks tombol UI
                const lowerT = t.toLowerCase();
                const lowerAuthor = author.toLowerCase();
                if (lowerT === lowerAuthor || lowerT === '@' + lowerAuthor) continue;
                if (lowerT === 'terjemahkan' || lowerT === 'translate' || lowerT === 'meta.ai') continue;
                
                // Abaikan teks berformat waktu (contoh: "1hari", "8 jam", "15 menit", "2 hari")
                if (lowerT.match(/^(\\d+\\s*(hari|jam|menit|detik|minggu|bulan|tahun|h|m|s|w|d|y)s?)$/)) continue;
                // Abaikan teks berformat tanggal (contoh: "24/09/2026", "11-09-2026")
                if (lowerT.match(/^\\d{1,2}[\\/\\-]\\d{1,2}[\\/\\-]\\d{2,4}$/)) continue;
                if (/^[\d.,kKmMrRbBjJtT\s]+$/.test(t)) continue; // Abaikan teks yang isinya cuma angka/satuan like
                if (span.closest('div[role="button"]')) continue; // Abaikan teks di dalam tombol
                
                contentArr.push(t);
            }
            let content = contentArr.join('\\n');
            if (!content || seen.has(content)) continue;
            seen.add(content);
            
            // === URL ===
            let url = '';
            const postLink = container.querySelector('a[href*="/post/"]');
            if (postLink) {
                const href = postLink.getAttribute('href') || '';
                url = href.startsWith('http') ? href : 'https://www.threads.net' + href;
            }
            
            // === ENGAGEMENT METRICS ===
            let likes = 0;
            let replies = 0;
            let shares = 0; 
            let views = 0; // Kembalikan views
            
            // Kita cari elemen div[role="button"] yang berada di bawah container
            // Tombol interaksi ini biasanya punya pola urutan tertentu jika text content dibaca.
            // Namun yang paling aman adalah mencari SVG dan judulnya.
            const svgs = container.querySelectorAll('svg');
            
            for (const svg of svgs) {
                const titleNode = svg.querySelector('title');
                const titleText = (titleNode ? titleNode.textContent : svg.getAttribute('aria-label') || '').toLowerCase();
                if (!titleText) continue;
                
                // Cari tombol interaksi yang membungkus SVG ini
                let btn = svg.closest('div[role="button"]');
                if (!btn) {
                    // Beberapa versi DOM Threads tidak pakai role="button", tapi div dengan tabindex
                    btn = svg.closest('div[tabindex="0"]');
                }
                
                if (!btn) continue;
                
                // Ambil semua text di dalam button tersebut (misal "Suka 12,8 rb" atau "1.2K")
                const rawText = btn.textContent || '';
                // Hapus nama judulnya (misal menghapus kata "Suka" sehingga tersisa "12,8 rb")
                // Hilangkan koma/titik sebagai pemisah ribuan agar aman
                let numStr = rawText.toLowerCase().replace(titleText.toLowerCase(), '').trim();
                
                if (!numStr) continue;
                
                let num = 0;
                // Parse angka, contoh: "35", "1.2K", "1,5M", "12,8 rb", "2,1 jt"
                const match = numStr.match(/([\d.,]+)\s*(k|m|rb|jt)?/);
                if (match) {
                    // ganti koma menjadi titik agar bisa di-parse float, khusus untuk desimal "12,8" -> "12.8"
                    // tapi hati-hati, jika "1.200" di Indonesia itu ribu.
                    let valStr = match[1];
                    // Aturan aman: 
                    // Jika ada K/M/rb/jt, maka , atau . adalah desimal (misal 1.2K atau 12,8 rb)
                    if (match[2]) {
                        valStr = valStr.replace(',', '.');
                        num = parseFloat(valStr);
                        if (match[2] === 'k' || match[2] === 'rb') num *= 1000;
                        else if (match[2] === 'm' || match[2] === 'jt') num *= 1000000;
                    } else {
                        // Jika tidak ada huruf satuan, maka koma/titik adalah pemisah ribuan (buang saja)
                        valStr = valStr.replace(/[.,]/g, '');
                        num = parseInt(valStr);
                    }
                }
                
                // Pastikan hanya ambil angka dari baris interaksi UTAMA (postingan, bukan balasan)
                // Kita batasi dengan mengecek !likes dsb untuk hanya mengisi nilai pertama
                if (titleText.includes('suka') || titleText.includes('like') || titleText.includes('heart')) {
                    if (likes === 0 && !isNaN(num)) likes = num;
                } else if (titleText.includes('komentar') || titleText.includes('repl') || titleText.includes('balas')) {
                    if (replies === 0 && !isNaN(num)) replies = num;
                } else if (titleText.includes('bagikan') || titleText.includes('share') || titleText.includes('kirim') || titleText.includes('send') || titleText.includes('pesawat')) {
                    if (shares === 0 && !isNaN(num)) shares = num;
                }
            }
            
            // === VIEWS (FALLBACK) ===
            // Cari elemen teks apa saja di dalam container yang berakhiran "views" atau "tayangan"
            if (views === 0) {
                const textNodes = container.querySelectorAll('span, div');
                for (const el of textNodes) {
                    const txt = (el.innerText || '').trim().toLowerCase();
                    const viewMatch = txt.match(/^([\\d.,]+)\\s*(k|m|rb|jt)?\\s*(views|tayangan)$/);
                    if (viewMatch) {
                        let valStr = viewMatch[1];
                        let num = 0;
                        if (viewMatch[2]) {
                            valStr = valStr.replace(',', '.');
                            num = parseFloat(valStr);
                            if (viewMatch[2] === 'k' || viewMatch[2] === 'rb') num *= 1000;
                            else if (viewMatch[2] === 'm' || viewMatch[2] === 'jt') num *= 1000000;
                        } else {
                            num = parseInt(valStr.replace(/[.,]/g, ''));
                        }
                        if (!isNaN(num)) {
                            views = num;
                            break;
                        }
                    }
                }
            }
            
            // === DATE ===
            let date = '';
            const timeEl = container.querySelector('time');
            if (timeEl) {
                date = timeEl.getAttribute('datetime') || timeEl.innerText || '';
            }
            if (!date) {
                const dateMatch = fullText.match(/(\\d{1,2}\\/\\d{1,2}\\/\\d{4}|\\d+\\s*(?:jam|hari|minggu|menit|detik|hours?|days?|weeks?)\\s*(?:yang lalu|ago)?)/i);
                if (dateMatch) date = dateMatch[1];
            }
            
            posts.push({
                content: content.substring(0, 500),
                author: author,
                likes: likes || 0,
                comments: replies || 0,
                shares: shares || 0,
                views: views || 0,
                url: url,
                date: date
            });
        }
    }
    
    // Fallback: jika selector utama gagal
    if (posts.length < 2) {
        const allSpans = document.querySelectorAll('span[dir="auto"]');
        for (const span of allSpans) {
            const text = span.innerText.trim();
            if (text && text.length > 30 && !seen.has(text)) {
                seen.add(text);
                
                let author = '';
                const usernameMatch = text.match(/^(\\w[\\w.]{1,30})\\s/);
                if (usernameMatch) author = usernameMatch[1];
                
                posts.push({
                    content: text.substring(0, 500),
                    author: author,
                    likes: 0,
                    comments: 0,
                    shares: 0,
                    views: 0,
                    url: '',
                    date: ''
                });
            }
        }
    }
    return posts;
    """
    
    while len(results) < max_results:
        try:
            # Ekstrak dari DOM yang sedang tampil
            extracted = THREADS_DRIVER.execute_script(extract_js)
            
            for post_data in extracted:
                if len(results) >= max_results:
                    break
                
                content = post_data.get("content", "")
                if not content or len(content) < 20:
                    continue
                
                # Bersihkan konten dari newline dan teks sampah
                content = content.replace('\n', ' ').replace('\r', ' ')
                content = re.sub(r'\s+', ' ', content).strip()
                # Hapus pola '1 / 2', 'Terjemahkan', 'meta.ai' dll di akhir teks
                # Kita gunakan regex yang lebih kuat untuk mengatasi sisa karakter aneh
                content = re.sub(r'(?:\s*\d+\s*/\s*\d+[^a-zA-Z0-9]*|\s*Terjemahkan\s*|\s*meta\.ai\s*)$', '', content, flags=re.IGNORECASE).strip()
                
                # Filter: skip jika konten terlalu pendek setelah cleaning
                if len(content) < 20:
                    continue
                
                # Cek duplikat
                if any(r['content'] == content for r in results):
                    continue
                    
                author = post_data.get("author", "") or "Threads_User"
                results.append({
                    "post_id": f"threads_{abs(hash(content)) % 1000000}",
                    "platform": "Threads",
                    "author": author,
                    "handle": f"@{author}" if author != "Threads_User" else "",
                    "content": content[:500],
                    "description": "",
                    "created_at": post_data.get("date", "") or datetime.now().isoformat(),
                    "likes": int(post_data.get("likes", 0)),
                    "shares": int(post_data.get("shares", 0)),
                    "comments": int(post_data.get("comments", 0)),
                    "views": int(post_data.get("views", 0)),
                    "url": post_data.get("url", ""),
                    "keyword": keyword,
                    "scraped_at": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"    [WARN] JS Extract error: {e}")
            pass
            
        if len(results) >= max_results:
            break
            
        # Scroll down
        THREADS_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        new_height = THREADS_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            new_height = THREADS_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    # === POST-PROCESSING: AMBIL VIEWS SATU PER SATU ===
    print(f"    [INFO] Mengambil angka 'views' untuk {len(results)} postingan (membuka tab satu per satu)...")
    try:
        main_window = THREADS_DRIVER.current_window_handle
        for i, r in enumerate(results):
            url = r.get("url")
            if not url:
                continue
            try:
                print(f"      - Cek views {i+1}/{len(results)}")
                THREADS_DRIVER.execute_script(f"window.open('{url}', '_blank');")
                # Pindah ke tab baru
                for handle in THREADS_DRIVER.window_handles:
                    if handle != main_window:
                        THREADS_DRIVER.switch_to.window(handle)
                        break
                
                time.sleep(3) # Tunggu halamannya loading
                
                views_js = """
                let v = 0;
                const els = document.querySelectorAll('span, div, h1, h2, h3, p');
                for(let el of els){
                    const txt = (el.innerText || '').trim().toLowerCase();
                    const match = txt.match(/^([\\d.,]+)\\s*(k|m|rb|jt)?\\s*(views|tayangan)$/);
                    if(match){
                        let valStr = match[1];
                        if (match[2]) {
                            valStr = valStr.replace(',', '.');
                            v = parseFloat(valStr);
                            const suf = match[2];
                            if(suf==='k'||suf==='rb') v*=1000;
                            else if(suf==='m'||suf==='jt') v*=1000000;
                        } else {
                            v = parseInt(valStr.replace(/[.,]/g, ''));
                        }
                        return v;
                    }
                }
                return 0;
                """
                v = THREADS_DRIVER.execute_script(views_js)
                if v:
                    r['views'] = int(v)
                else:
                    r['views'] = 0
                    
                THREADS_DRIVER.close() # Tutup tab
                THREADS_DRIVER.switch_to.window(main_window) # Kembali ke tab utama
                time.sleep(1) # Jeda antar klik
            except Exception as e:
                print(f"      [WARN] Gagal ambil views: {e}")
                try:
                    if len(THREADS_DRIVER.window_handles) > 1:
                        THREADS_DRIVER.close()
                    THREADS_DRIVER.switch_to.window(main_window)
                except:
                    pass
    except Exception as e:
        print(f"    [WARN] Error saat memproses views: {e}")

    return results

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Threads (Selenium)...")
    data = scrape_threads("makan bergizi gratis", max_results=5)
    print(f"Berhasil ambil {len(data)} data")
    for d in data:
        print(f"  - Likes: {d['likes']}, Comments: {d['comments']}, Author: {d['author']}")
        print(f"    Content: {d['content'][:80]}...")
    if THREADS_DRIVER:
        THREADS_DRIVER.quit()

