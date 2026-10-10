import os
import sys
import time
import pandas as pd

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from cell_02_config import TOPICS, OUTPUT_DIR
from cell_06_news import scrape_news, NEWS_EXTRA_KEYWORDS

print("=" * 60)
print("MEMULAI SCRAPING NEWS (Google News + Bing News)")
print("Target: ~16.000 artikel")
print("=" * 60)

# Gabungkan TOPICS + NEWS_EXTRA_KEYWORDS
all_keywords = {}
for topic, keywords in TOPICS.items():
    combined = list(keywords)  # copy
    if topic in NEWS_EXTRA_KEYWORDS:
        for kw in NEWS_EXTRA_KEYWORDS[topic]:
            if kw not in combined:
                combined.append(kw)
    all_keywords[topic] = combined

total_keywords = sum(len(kws) for kws in all_keywords.values())
print(f"[INFO] Total keywords (original + extra): {total_keywords}")

all_results = []
current_kw = 1
temp_path = os.path.join(OUTPUT_DIR, "scraped_News_Only.csv")
existing_keywords = set()

# AUTO-RESUME: Cek CSV yang sudah ada
if os.path.exists(temp_path):
    try:
        df_existing = pd.read_csv(temp_path)
        existing_keywords = set(df_existing['keyword'].dropna().unique())
        all_results = df_existing.to_dict('records')
        print(f"[INFO] Melanjutkan dari file yang ada! ({len(existing_keywords)} keyword sudah selesai)")
    except Exception as e:
        print(f"[WARN] Gagal membaca CSV lama: {e}")

for topic, keywords in all_keywords.items():
    print(f"\n{'='*40}")
    print(f"[{topic}] Memproses {len(keywords)} keyword...")
    print(f"{'='*40}")
    
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        
        # SKIP JIKA SUDAH ADA DI CSV
        if kw in existing_keywords:
            print(f"  [SKIP] Keyword '{kw}' sudah di-scrape sebelumnya.")
            current_kw += 1
            continue
        
        try:
            data = scrape_news(kw)
            for d in data:
                d['topic'] = topic
            all_results.extend(data)
            print(f"  [OK] {len(data)} artikel (Google + Bing) untuk '{kw}'")
        except Exception as e:
            print(f"  [ERROR] Gagal scrape '{kw}': {e}")
        
        current_kw += 1

        # Simpan incremental setiap 5 keywords
        if current_kw % 5 == 0 or current_kw == total_keywords:
            df_temp = pd.DataFrame(all_results)
            # Deduplikasi berdasarkan URL
            df_temp.drop_duplicates(subset=['url'], inplace=True)
            # Deduplikasi berdasarkan judul (content) yang persis sama
            df_temp.drop_duplicates(subset=['content'], inplace=True)
            df_temp.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [SAVE] {len(df_temp)} artikel unik tersimpan")

# Final save
df_final = pd.DataFrame(all_results)
df_final.drop_duplicates(subset=['url'], inplace=True)
df_final.drop_duplicates(subset=['content'], inplace=True)
df_final.to_csv(temp_path, index=False, encoding='utf-8-sig')

print(f"\n{'='*60}")
print(f"SELESAI! Total {len(df_final)} artikel unik disimpan ke:")
print(temp_path)
print(f"\nDistribusi topik:")
print(df_final['topic'].value_counts().to_string())
if 'source' in df_final.columns:
    print(f"\nDistribusi sumber:")
    print(df_final['source'].value_counts().to_string())
print("=" * 60)
