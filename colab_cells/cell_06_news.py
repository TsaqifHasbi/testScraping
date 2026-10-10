from cell_02_config import *
# ============================================================
# CELL 6: SCRAPER NEWS (Google News RSS + Bing News RSS)
# Tools: feedparser (Ringan, Cepat, Bebas Rate-Limit)
# Target: ~16.000 artikel
# ============================================================

from datetime import datetime, timedelta, timezone
import time
import re
import html
import urllib.parse
# pyrefly: ignore [missing-import]
import feedparser

# Timezone WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

def _parse_date_to_wib(date_str):
    """Parse tanggal dari RSS feed dan konversi ke WIB."""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        dt_wib = dt.astimezone(WIB)
        return dt_wib.strftime("%Y-%m-%d %H:%M:%S WIB")
    except:
        pass
    
    # Fallback: coba format umum
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_wib = dt.astimezone(WIB)
            return dt_wib.strftime("%Y-%m-%d %H:%M:%S WIB")
        except:
            continue
    
    return date_str


def _clean_title(title, pub_name=""):
    """Bersihkan judul dari nama publisher yang menempel di akhir."""
    if not title:
        return title
    # Hapus " - Publisher" di akhir judul
    if pub_name and title.endswith(f" - {pub_name}"):
        title = title[: -(len(f" - {pub_name}"))].strip()
    elif " - " in title:
        parts = title.rsplit(" - ", 1)
        # Hanya hapus jika bagian terakhir pendek (nama publisher)
        if len(parts) > 1 and len(parts[1]) < 50:
            title = parts[0].strip()
    return title


def _scrape_google_news(keyword, max_results=100):
    """Scrape dari Google News RSS Feed."""
    results = []
    seen_urls = set()

    try:
        query = urllib.parse.quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
        
        feed = feedparser.parse(rss_url)
        
        for idx, entry in enumerate(feed.entries):
            url = entry.get("link", "")
            title = entry.get("title", "")
            
            if url in seen_urls or not title:
                continue
            seen_urls.add(url)
            
            # Ambil nama publisher
            pub_name = ""
            source_obj = getattr(entry, "source", None)
            if source_obj and hasattr(source_obj, "get"):
                pub_name = source_obj.get("title", "")
            elif isinstance(source_obj, dict):
                pub_name = source_obj.get("title", "")
            
            if not pub_name and " - " in title:
                parts = title.rsplit(" - ", 1)
                if len(parts) > 1 and len(parts[1]) < 50:
                    pub_name = parts[1].strip()
            
            if not pub_name:
                pub_name = "Berita Online"
            
            # Bersihkan judul
            clean = _clean_title(title, pub_name)
            
            # Handle
            handle_name = f"@{pub_name.lower().replace(' ', '').replace('.', '_')}"
            
            # Parse tanggal ke WIB
            raw_date = entry.get("published", "")
            created_at = _parse_date_to_wib(raw_date) if raw_date else datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
            
            # FILTER TANGGAL: 1 Januari 2025 - Sekarang
            if created_at < "2025-01-01 00:00:00 WIB":
                continue
            
            # Bersihkan summary
            summary = entry.get("summary", "")
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            summary = html.unescape(summary)
            
            results.append({
                "post_id": f"news_google_{idx}_{abs(hash(url)) % 1000000}",
                "platform": "News",
                "source": "Google News",
                "author": pub_name,
                "handle": handle_name,
                "content": clean,
                "description": summary[:1000] if summary else "",
                "created_at": created_at,
                "url": url,
                "keyword": keyword,
                "scraped_at": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
            })
            
    except Exception as e:
        print(f"      [!] Google News error: {str(e)[:80]}")

    return results


def _scrape_bing_news(keyword, max_results=100):
    """Scrape dari Bing News RSS Feed."""
    results = []
    seen_urls = set()

    try:
        query = urllib.parse.quote(keyword)
        # Bing News RSS - format=rss, cc=ID untuk Indonesia
        rss_url = f"https://www.bing.com/news/search?q={query}&format=rss&cc=ID&setlang=id"
        
        feed = feedparser.parse(rss_url)
        
        for idx, entry in enumerate(feed.entries):
            url = entry.get("link", "")
            title = entry.get("title", "")
            
            if url in seen_urls or not title:
                continue
            seen_urls.add(url)
            
            # Publisher dari news_source (khusus Bing) atau title
            pub_name = entry.get("news_source", "")
            
            if not pub_name and " - " in title:
                parts = title.rsplit(" - ", 1)
                if len(parts) > 1 and len(parts[1]) < 50:
                    pub_name = parts[1].strip()
            
            if not pub_name:
                pub_name = "Berita Online"
            
            # Bersihkan judul
            clean = _clean_title(title, pub_name)
            
            # Handle
            handle_name = f"@{pub_name.lower().replace(' ', '').replace('.', '_')}"
            
            # Parse tanggal ke WIB
            raw_date = entry.get("published", "")
            created_at = _parse_date_to_wib(raw_date) if raw_date else datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
            
            # FILTER TANGGAL: 1 Januari 2025 - Sekarang
            if created_at < "2025-01-01 00:00:00 WIB":
                continue
            
            # Description
            summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            summary = html.unescape(summary)
            
            results.append({
                "post_id": f"news_bing_{idx}_{abs(hash(url)) % 1000000}",
                "platform": "News",
                "source": "Bing News",
                "author": pub_name,
                "handle": handle_name,
                "content": clean,
                "description": summary[:1000] if summary else "",
                "created_at": created_at,
                "url": url,
                "keyword": keyword,
                "scraped_at": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
            })
            
    except Exception as e:
        print(f"      [!] Bing News error: {str(e)[:80]}")

    return results


def scrape_news(keyword, max_results=100):
    """
    Scrape berita dari Google News RSS + Bing News RSS.
    Menggabungkan dua sumber untuk memaksimalkan kuantitas data.
    """
    # Scrape dari kedua sumber
    google_results = _scrape_google_news(keyword, max_results=max_results)
    bing_results = _scrape_bing_news(keyword, max_results=max_results)
    
    # Gabungkan dan deduplikasi berdasarkan URL
    combined = google_results + bing_results
    seen = set()
    unique = []
    for r in combined:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    
    return unique


# ============================================================
# KEYWORD EKSPANSI OTOMATIS UNTUK NEWS
# Keyword tambahan khusus News untuk menaikkan kuantitas
# ============================================================
NEWS_EXTRA_KEYWORDS = {
    "MBG": [
        # Keyword daerah
        "MBG Jakarta", "MBG Jawa Tengah", "MBG Jawa Barat", "MBG Jawa Timur",
        "MBG Sumatera", "MBG Kalimantan", "MBG Sulawesi", "MBG Papua",
        "MBG Bali", "MBG NTT", "MBG NTB",
        # Keyword spesifik isu
        "korupsi MBG", "korupsi makan bergizi gratis",
        "MBG SPPG", "dapur MBG", "mitra dapur MBG",
        "insentif MBG", "MBG sekolah", "MBG madrasah",
        "MBG puskesmas", "MBG posyandu",
        "makan bergizi gratis 2026", "MBG 2026",
        "kasus MBG", "tersangka MBG", "kejagung MBG",
        "Dadan Hindayana korupsi", "BGN korupsi",
        "gizi anak Indonesia", "program gizi sekolah",
        "makanan gratis pelajar", "makan siang gratis sekolah",
        "anggaran makan bergizi", "dana MBG",
        "evaluasi MBG", "MBG pro kontra",
        "makan bergizi gratis viral", "MBG berita terbaru",
        "keracunan makanan sekolah", "food poisoning MBG",
    ],
    "KDMP": [
        # Keyword daerah
        "koperasi desa Jawa", "koperasi desa Sumatera", "koperasi desa Kalimantan",
        "koperasi desa Sulawesi", "koperasi desa Papua",
        # Keyword spesifik isu
        "BUMDes koperasi desa", "BUMDes merah putih",
        "koperasi desa prabowo gibran", "koperasi desa 2026",
        "KDMP 2026", "koperasi desa toko kelontong",
        "koperasi desa alfamart indomaret",
        "koperasi desa ekonomi rakyat", "koperasi desa petani",
        "koperasi desa nelayan", "koperasi desa UMKM digital",
        "koperasi desa modal usaha", "koperasi desa pinjaman",
        "koperasi desa simpan pinjam", "koperasi merah putih berita",
        "koperasi desa berita terbaru", "koperasi desa kontroversi terbaru",
        "KDMP evaluasi", "KDMP pro kontra",
        "koperasi desa pro kontra", "koperasi rakyat merah putih",
        "KDMP Kemendes", "koperasi desa Kemendes",
        "koperasi desa bantuan modal",
    ],
    "Sekolah_Rakyat": [
        # Keyword daerah
        "sekolah rakyat Jakarta", "sekolah rakyat Jawa",
        "sekolah rakyat Sumatera", "sekolah rakyat Kalimantan",
        "sekolah rakyat Sulawesi", "sekolah rakyat Papua",
        # Keyword spesifik isu
        "sekolah rakyat 2026", "sekolah rakyat Kemensos",
        "sekolah rakyat anak putus sekolah", "sekolah rakyat anak jalanan",
        "sekolah rakyat daerah 3T", "sekolah rakyat terpencil",
        "sekolah rakyat berita terbaru", "sekolah rakyat pendaftaran 2026",
        "sekolah rakyat asrama murid", "sekolah rakyat asrama gratis",
        "sekolah rakyat evaluasi", "sekolah rakyat pro kontra",
        "program pendidikan rakyat gratis", "program sekolah gratis 2026",
        "sekolah rakyat Nadiem Makarim", "sekolah rakyat kurikulum merdeka",
        "sekolah rakyat anggaran", "sekolah rakyat dana pendidikan",
        "sekolah gratis pemerintah prabowo", "sekolah rakyat vokasi",
        "sekolah rakyat SMA", "sekolah rakyat SD",
    ],
}


# ============================================================
# TEST (hanya jika dijalankan langsung)
# ============================================================
if __name__ == "__main__":
    print("[TEST] Menguji News scraper (Google + Bing)...")
    test = scrape_news("Makan Bergizi Gratis", max_results=5)
    print(f"[OK] News: {len(test)} artikel ditemukan")
    for t in test:
        src = t.get('source', '?')
        print(f"   [{src}] {t['content'][:60]}...")
        print(f"      Publisher: {t['author']} | Handle: {t['handle']} | Tanggal: {t['created_at']}")
