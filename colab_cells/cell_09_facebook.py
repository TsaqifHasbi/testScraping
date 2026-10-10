# ============================================================
# CELL 9: SCRAPING FACEBOOK (SELENIUM UNDETECTED)
# ============================================================
import time
import os
import re
import urllib.parse
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

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

FB_DRIVER = None


def _clean_text(text):
    """Membersihkan teks dari artefak UI Facebook dan karakter baris baru."""
    # Hapus tombol-tombol UI
    for junk in ['See less', 'See more', 'See Less', 'See More',
                 'Lihat selengkapnya', 'Sembunyikan',
                 'See translation', 'See Translation',
                 'Lihat Terjemahan', 'Translated by Meta AI']:
        text = text.replace(junk, '')
    
    # Ganti newline dan carriage return menjadi spasi agar tidak merusak format CSV
    text = re.sub(r'[\r\n]+', ' ', text)
    # Collapse spasi berlebih
    text = re.sub(r' +', ' ', text).strip()
    return text


def _clean_engagement(raw):
    """Membersihkan string angka engagement dan mengkonversi ke nominal asli."""
    if not raw:
        return "0"
    raw = raw.strip()
    # Mengonversi teks seperti "27K" menjadi "27000" sesuai permintaan user
    return parse_eng(raw)


def _extract_via_js(driver):
    """
    Menggunakan JavaScript untuk mengekstrak data post langsung dari DOM.
    Ini JAUH lebih akurat daripada BeautifulSoup karena bisa membaca
    elemen yang sudah di-render oleh React/JS Facebook.
    """
    script = """
    // Cari semua elemen post. Di Facebook Search, setiap post ada di dalam
    // elemen dengan role="article" ATAU di dalam div yang mengandung h3/h4.
    let posts = [];
    
    // Strategi: Cari semua div[role="article"] 
    let articles = document.querySelectorAll('div[role="article"]');
    
    // Jika tidak ada article, cari alternatif (FB kadang tidak pakai role="article")
    if (articles.length === 0) {
        // Fallback: cari semua h3 lalu panjat ke atas
        let headers = document.querySelectorAll('h3, h4');
        let containers = new Set();
        headers.forEach(h => {
            let p = h;
            for (let i = 0; i < 8; i++) {
                if (p.parentElement) p = p.parentElement;
            }
            containers.add(p);
        });
        articles = Array.from(containers);
    }
    
    for (let article of articles) {
        let post = {};
        
        // 1. AUTHOR: Cari dari header artikel agar tidak salah menangkap nama grup
        let headerDiv = article.querySelector('div[data-ad-preview="message"]')?.parentElement?.previousElementSibling || article;
        let headerLinks = Array.from(headerDiv.querySelectorAll('h2 a[role="link"], h3 a[role="link"], h4 a[role="link"], a[role="link"], a[tabindex="0"]'))
            .filter(a => a.innerText.trim().length > 0 && !/(like|comment|share|follow|bergabung|suka|komentar|bagikan)/i.test(a.innerText));
        
        // Helper untuk membersihkan "Online status indicator"
        let extractCleanName = (txt) => {
            if (!txt) return '';
            let lines = txt.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            return lines.find(l => !/^(Online status indicator|Active)$/i.test(l)) || '';
        };

        post.author = '';
        if (headerLinks.length > 0) {
            // Biasanya author adalah link pertama.
            post.author = extractCleanName(headerLinks[0].innerText);
            // Tapi jika link pertama adalah nama grup (mengandung /groups/), kita coba ambil link kedua sebagai author sebenarnya
            if (headerLinks[0].href.includes('/groups/') && headerLinks.length > 1) {
                let altName = extractCleanName(headerLinks[1].innerText);
                if (altName) post.author = altName;
            }
        }
        
        // Fallback jika tidak ditemukan
        if (!post.author) {
            let authorEls = article.querySelectorAll('h2, h3, h4, strong');
            for (let el of authorEls) {
                let name = extractCleanName(el.innerText);
                if (name) {
                    post.author = name;
                    break;
                }
            }
        }
        
        // Skip jika author kosong atau terlalu pendek
        if (post.author.length < 2) continue;
        
        // 2. CONTENT: Ambil SEMUA div[dir="auto"] di dalam article
        let contentDivs = article.querySelectorAll('div[dir="auto"]');
        let seenTexts = new Set();
        let contentParts = [];
        
        for (let cd of contentDivs) {
            let txt = cd.innerText.trim();
            // Skip jika teks terlalu pendek atau sudah ada
            if (txt.length < 15) continue;
            
            // Skip teks yang merupakan bagian dari teks lain (deduplikasi)
            let dominated = false;
            for (let existing of seenTexts) {
                if (existing.includes(txt.substring(0, 30))) {
                    dominated = true;
                    break;
                }
            }
            if (dominated) continue;
            
            // Hapus teks yang didominasi oleh teks baru ini
            let newSeen = new Set();
            for (let existing of seenTexts) {
                if (!txt.includes(existing.substring(0, 30))) {
                    newSeen.add(existing);
                } else {
                    // Existing sudah termasuk di txt baru, hapus dari contentParts
                    contentParts = contentParts.filter(p => !p.startsWith(existing.substring(0, 30)));
                }
            }
            newSeen.add(txt);
            seenTexts = newSeen;
            contentParts.push(txt);
        }
        
        post.content = contentParts.join('\\n\\n').trim();
        
        // Skip jika content kosong
        if (post.content.length < 20) continue;
        
        // 3. URL: Cari link terbaik
        let allLinks = article.querySelectorAll('a[href]');
        let validLinks = Array.from(allLinks)
            .map(a => a.getAttribute('href') || '')
            .filter(href => href && href !== '#' && !href.includes('dialog/share') && !href.includes('sharer.php') && !href.includes('hovercard') && !href.includes('hashtag/') && !href.includes('/groups/search/'));
            
        let bestLink = validLinks.find(h => (h.includes('/posts/') || h.includes('/permalink/') || h.includes('fbid=')) && h.includes('__cft__'));
        if (!bestLink) bestLink = validLinks.find(h => h.includes('/posts/') || h.includes('/permalink/'));
        if (!bestLink) bestLink = validLinks.find(h => h.includes('fbid=') || h.includes('story_fbid='));
        if (!bestLink) bestLink = validLinks.find(h => h.includes('/groups/') && h.includes('/user/') === false);
        if (!bestLink) bestLink = validLinks.find(h => h.includes('/videos/') || h.includes('/reel/'));
        if (!bestLink) bestLink = validLinks.find(h => h.includes('/photo/'));
        if (!bestLink) bestLink = validLinks.find(h => h.includes('__cft__') && !h.includes('/user/'));
        if (!bestLink && validLinks.length > 0) bestLink = validLinks[0]; // Absolute fallback
        
        post.url = bestLink || 'https://www.facebook.com/';
        
        // Bersihkan parameter tracking Facebook yang panjang & jelek
        if (post.url.includes('?__cft__')) {
            post.url = post.url.split('?__cft__')[0];
        } else if (post.url.includes('&__cft__')) {
            post.url = post.url.split('&__cft__')[0];
        }
        
        if (post.url && !post.url.startsWith('http')) {
            post.url = 'https://www.facebook.com' + post.url;
        }
        
        // 4. ENGAGEMENT: Cari dari aria-label dan DOM traverse
        post.likes = '0';
        post.comments = '0';
        post.shares = '0';
        
        // Metode A: Cari elemen dengan aria-label
        let allEls = article.querySelectorAll('*[aria-label]');
        for (let el of allEls) {
            let label = el.getAttribute('aria-label').toLowerCase();
            let numMatch = label.match(/([\\.\\d,]+\\s*(?:k|m|rb|ribu|jt|juta)?)/i);
            if (!numMatch) continue;
            let numStr = numMatch[1];
            
            if (/(suka|like|reaksi|reaction)/i.test(label)) {
                if (post.likes === '0') post.likes = numStr;
            } else if (/(komentar|comment)/i.test(label)) {
                if (post.comments === '0') post.comments = numStr;
            } else if (/(bagikan|share)/i.test(label)) {
                if (post.shares === '0') post.shares = numStr;
            }
        }
        
        // Metode B: Traverse langsung pada Action Row untuk menangkap teks div/span
        let likeBtn = Array.from(article.querySelectorAll('div[role="button"], div[tabindex="0"], span')).find(b => /^(Like|Suka)$/i.test(b.innerText?.trim()));
        if (likeBtn) {
            // Container Action Toolbar biasanya ada 2-3 level di atas Like
            let actionRow = likeBtn.closest('div.x1n2onr6, div.x1y1aw1k') || likeBtn.parentElement.parentElement;
            // Baris angka engagement biasanya adalah previous sibling dari Action Toolbar
            let engagementRow = actionRow ? actionRow.previousElementSibling : null;
            
            if (engagementRow) {
                let text = engagementRow.innerText || '';
                
                // Cek eksplisit dengan indikator
                let cm = text.match(/([\\.\\d,]+\\s*(?:k|m|rb|ribu|jt|juta)?)\\s*(comments?|komentar)/i);
                if (cm && post.comments === '0') post.comments = cm[1];
                
                let sm = text.match(/([\\.\\d,]+\\s*(?:k|m|rb|ribu|jt|juta)?)\\s*(shares?|kali dibagikan|bagikan)/i);
                if (sm && post.shares === '0') post.shares = sm[1];
                
                // Ambil semua token angka bebas yang ada (dipisahkan spasi atau newline)
                let tokens = text.split(/[\\n\\s]+/);
                let nums = tokens.filter(t => /^[\\.\\d,]+(?:k|m|rb|ribu|jt|juta)?$/i.test(t));
                nums = [...new Set(nums)]; // Hapus duplikat
                
                // Assign sisa angka bebas secara berurutan: likes, comments, shares
                if (post.likes === '0' && nums.length >= 1) post.likes = nums[0];
                if (post.comments === '0' && nums.length >= 2) post.comments = nums[1];
                if (post.shares === '0' && nums.length >= 3) post.shares = nums[2];
            }
        }
        
        // Metode C: Teks langsung regex keseluruhan (sebagai fallback terakhir)
        let fullText = article.innerText;
        if (post.likes === '0') {
            let m = fullText.match(/([\\.\\d,]+\\s*(?:K|M|rb|ribu|jt|juta)?)\\s*(?:suka|like|reaksi|people like this)/i);
            if (m) post.likes = m[1];
        }
        if (post.comments === '0') {
            let m = fullText.match(/([\\.\\d,]+\\s*(?:K|M|rb|ribu|jt|juta)?)\\s*(?:komentar|comments?)/i);
            if (m) post.comments = m[1];
        }
        if (post.shares === '0') {
            let m = fullText.match(/([\\.\\d,]+\\s*(?:K|M|rb|ribu|jt|juta)?)\\s*(?:kali dibagikan|shares?|bagikan)/i);
            if (m) post.shares = m[1];
        }
        
        // Metode D: Trailing Numbers (Menangkap UI FB Baru yang hanya ikon tanpa teks label)
        let ignoreRegex = /^(Like|Suka|Comment|Komentar|Share|Bagikan|Send|Kirim|See more|Lihat selengkapnya|See translation|Lihat terjemahan|Original text|Lihat teks asli|Hide|Sembunyikan|Write a comment|Tulis komentar.*)$/i;
        let lines = (article.innerText || '').split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        let trailingNums = [];
        for (let i = lines.length - 1; i >= 0; i--) {
            let line = lines[i];
            // Jika baris berisi angka murni (termasuk k, rb, jt) dan panjangnya logis
            if (/^[\\.\\d,]+\\s*(?:k|m|rb|ribu|jt|juta)?$/i.test(line) && line.length <= 12) {
                trailingNums.unshift(line);
            } else if (!ignoreRegex.test(line)) {
                // Berhenti mencari jika menemukan teks normal
                break;
            }
        }
        if (trailingNums.length > 0) {
            if (post.likes === '0') post.likes = trailingNums[0];
            if (post.comments === '0' && trailingNums.length > 1) post.comments = trailingNums[1];
            if (post.shares === '0' && trailingNums.length > 2) post.shares = trailingNums[2];
        }
        
        posts.push(post);
    }
    
    return posts;
    """
    try:
        return driver.execute_script(script)
    except Exception as e:
        print(f"    [WARN] JS extraction failed: {e}")
        return []


def scrape_facebook(keyword, max_results=100):
    global FB_DRIVER

    print(f"    - Facebook Selenium: mencari '{keyword}'...")

    if FB_DRIVER is None:
        print("    [!] Membuka Chrome untuk Facebook pertama kali...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--disable-notifications")
        FB_DRIVER = uc.Chrome(options=options, version_main=153)

        FB_DRIVER.get("https://www.facebook.com/login")
        print("\n" + "="*60)
        print("🚨 TINDAKAN DIBUTUHKAN (FACEBOOK) 🚨")
        print("1. Jendela Chrome sudah terbuka.")
        print("2. Silakan LOGIN dan SELESAIKAN CAPTCHA/2FA secara MANUAL.")
        print("3. JANGAN tekan Enter sebelum Anda benar-benar masuk ke Beranda FB!")
        print("="*60 + "\n")
        input("👉 TEKAN ENTER DI SINI JIKA SUDAH SELESAI LOGIN & CAPTCHA... ")
        print("    [OK] Melanjutkan ke pencarian...")
        time.sleep(2)

    # Mulai Pencarian
    query = urllib.parse.quote(keyword)
    url = f"https://www.facebook.com/search/posts/?q={query}"

    try:
        FB_DRIVER.get(url)
    except Exception as e:
        print(f"    [ERROR] Gagal membuka URL: {e}")
        return []
        
    time.sleep(5)

    results = []
    last_height = FB_DRIVER.execute_script("return document.body.scrollHeight")

    for scroll_round in range(10):  # Maksimal 10 kali scroll
        if len(results) >= max_results:
            break

        # PAKSA BUKA SEMUA TOMBOL "SEE MORE" DAN "SEE ORIGINAL"
        expand_js = """
        document.querySelectorAll('div[role="button"], span, div').forEach(el => {
            let txt = (el.innerText || '').trim().toLowerCase();
            if (txt === 'see more' || txt === 'lihat selengkapnya' || txt === 'selengkapnya' || txt === 'see more...') {
                try { el.click(); } catch(e) {}
            }
            if (txt === 'see original' || txt === 'lihat teks asli' || txt === 'lihat yang asli' || txt === 'original text') {
                try { el.click(); } catch(e) {}
            }
        });
        """
        try:
            FB_DRIVER.execute_script(expand_js)
            time.sleep(1.5)
        except:
            pass

        # Ekstrak data via JavaScript (jauh lebih akurat dari BS4)
        raw_posts = _extract_via_js(FB_DRIVER)

        for post in raw_posts:
            if len(results) >= max_results:
                break

            author = post.get('author', '')
            content = post.get('content', '')
            url_post = post.get('url', '')

            # Bersihkan author
            author = re.sub(r'·\s*Join|·\s*Follow|·', '', author, flags=re.IGNORECASE).strip()
            author = re.split(r'(?i)(is at |is in |sedang di )', author)[0].strip()
            # Potong max 50 karakter
            author = author[:50]

            # Bersihkan content
            content = _clean_text(content)
            if len(content) < 20:
                continue

            # Bersihkan engagement
            likes = _clean_engagement(post.get('likes', '0'))
            comments = _clean_engagement(post.get('comments', '0'))
            shares = _clean_engagement(post.get('shares', '0'))

            # Cek duplikasi berdasarkan 60 karakter pertama content
            content_key = content[:60]
            if any(content_key in r['content'][:60] for r in results):
                continue

            results.append({
                "platform": "Facebook",
                "topic": "UNKNOWN",
                "content": content,
                "author": author,
                "url": url_post,
                "likes": likes,
                "comments": comments,
                "shares": shares
            })
            print(f"  -> Terambil FB | {author[:15]} | L:{likes} C:{comments} S:{shares} | {url_post[:40]}...")

        # Scroll ke bawah
        FB_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        new_height = FB_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            new_height = FB_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    return results


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("[TEST] Memulai test scrape Facebook (Selenium)...")
    data = scrape_facebook("makan bergizi gratis", max_results=10)
    print(f"Berhasil ambil {len(data)} data")
    if FB_DRIVER:
        FB_DRIVER.quit()
