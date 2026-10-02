import os
import csv
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_09_facebook import scrape_facebook

print("="*60)
print("[START] MEMULAI SCRAPING FACEBOOK ONLY")
print("="*60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")

    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")

        try:
            data = scrape_facebook(kw, max_results=30)
        except Exception as e:
            print(f"    [ERROR] {e}")
            data = []

        for d in data:
            d['topic'] = topic

        all_results.extend(data)
        current_kw += 1

        # Simpan progres setiap keyword (menggunakan csv module untuk quoting)
        df_temp = pd.DataFrame(all_results)
        if len(df_temp) > 0:
            df_temp.drop_duplicates(subset=['content'], keep='first', inplace=True)
            temp_path = os.path.join(OUTPUT_DIR, "scraped_Facebook_Only.csv")
            try:
                df_temp.to_csv(
                    temp_path,
                    index=False,
                    sep=',',
                    quoting=csv.QUOTE_MINIMAL,
                    encoding='utf-8-sig'         # BOM agar Excel baca UTF-8
                )
            except PermissionError:
                print(f"    [WARNING] File CSV sedang dibuka di aplikasi lain, gagal auto-save.")

print("\n" + "="*60)
print(f"[DONE] SELESAI! Total {len(all_results)} data Facebook berhasil disimpan.")
print("="*60)
