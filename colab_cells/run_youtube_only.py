import os
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_03_youtube import scrape_youtube

print("="*60)
print("🚀 MEMULAI SCRAPING YOUTUBE ONLY")
print("="*60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

temp_path = os.path.join(OUTPUT_DIR, "scraped_YouTube_Only.csv")
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

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        
        # SKIP JIKA SUDAH ADA DI CSV
        if kw in existing_keywords:
            print(f"  [SKIP] Keyword '{kw}' sudah di-scrape sebelumnya.")
            current_kw += 1
            continue

        data = scrape_youtube(kw)
        
        if data:
            for d in data: d['topic'] = topic
            all_results.extend(data)

        current_kw += 1

        df_temp = pd.DataFrame(all_results)
        if 'url' in df_temp.columns:
            df_temp.drop_duplicates(subset=['url'], inplace=True)
        df_temp.to_csv(temp_path, index=False)
        print(f"  [OK] Tersimpan! Total data di CSV: {len(df_temp)}")

print("\n🎉 SELESAI! YouTube berhasil disimpan.")
