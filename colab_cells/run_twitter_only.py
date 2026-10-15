import os
import sys
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_04_twitter import scrape_twitter, load_seen_urls, reset_tracking

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

print("=" * 60)
print("🚀 MEMULAI SCRAPING TWITTER/X (FULL CRAWL)")
print("📅 Filter: 1 Januari 2025 - Sekarang")
print("🔄 Auto-Resume: Ya")
print("=" * 60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

temp_path = os.path.join(OUTPUT_DIR, "scraped_Twitter_Only.csv")
existing_keywords = set()

# AUTO-RESUME: Cek CSV yang sudah ada
if os.path.exists(temp_path):
    try:
        df_existing = pd.read_csv(temp_path)
        existing_keywords = set(df_existing['keyword'].dropna().unique())
        all_results = df_existing.to_dict('records')

        # Load existing URLs untuk deduplikasi global
        if 'url' in df_existing.columns:
            existing_urls = set(df_existing['url'].dropna().unique())
            load_seen_urls(existing_urls)

        print(f"[INFO] Melanjutkan dari file yang ada!")
        print(f"       - {len(existing_keywords)} keyword sudah selesai")
        print(f"       - {len(all_results)} data sudah tersimpan")
    except Exception as e:
        print(f"[WARN] Gagal membaca CSV lama: {e}")
        reset_tracking()
else:
    reset_tracking()

for topic, keywords in TOPICS.items():
    print(f"\n{'=' * 40}")
    print(f"[{topic}] Memproses {len(keywords)} keyword...")
    print(f"{'=' * 40}")

    for i, kw in enumerate(keywords):
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")

        # SKIP JIKA SUDAH ADA DI CSV
        if kw in existing_keywords:
            print(f"  [SKIP] Keyword '{kw}' sudah di-scrape sebelumnya.")
            current_kw += 1
            continue

        try:
            # 2 keyword utama per topik ambil 1000, sisanya 100
            target_results = 1000 if i < 2 else 100
            data = scrape_twitter(kw, max_results=target_results)

            for d in data:
                d['topic'] = topic

            all_results.extend(data)

            # SIMPAN LANGSUNG + DEDUPLIKASI by URL
            df_temp = pd.DataFrame(all_results)
            if 'url' in df_temp.columns:
                before = len(df_temp)
                df_temp = df_temp.drop_duplicates(subset=['url'], keep='first')
                removed = before - len(df_temp)
                if removed > 0:
                    print(f"  [DEDUP] Dihapus {removed} duplikat URL.")
                    all_results = df_temp.to_dict('records')

            df_temp.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [OK] Tersimpan! Total data di CSV: {len(df_temp)}")

        except Exception as e:
            print(f"  [ERROR] Scraping gagal pada keyword '{kw}': {e}")
            print("  [INFO] Merestart Chrome untuk keyword berikutnya...")
            import cell_04_twitter
            try:
                cell_04_twitter._init_driver()
            except:
                cell_04_twitter.TWITTER_DRIVER = None

        current_kw += 1

# Final dedup & save
df_final = pd.DataFrame(all_results)
if 'url' in df_final.columns and len(df_final) > 0:
    df_final = df_final.drop_duplicates(subset=['url'], keep='first')
df_final.to_csv(temp_path, index=False, encoding='utf-8-sig')

print(f"\n{'=' * 60}")
print(f"🎉 SELESAI! Total {len(df_final)} data Twitter unik berhasil disimpan ke:")
print(temp_path)
if 'topic' in df_final.columns and len(df_final) > 0:
    print(f"\nDistribusi topik:")
    print(df_final['topic'].value_counts().to_string())
print("=" * 60)
