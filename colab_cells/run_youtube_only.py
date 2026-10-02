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

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        data = scrape_youtube(kw, max_results=50)
        for d in data: d['topic'] = topic
        all_results.extend(data)
        current_kw += 1

        df_temp = pd.DataFrame(all_results)
        df_temp.drop_duplicates(subset=['url'], inplace=True)
        temp_path = os.path.join(OUTPUT_DIR, "scraped_YouTube_Only.csv")
        df_temp.to_csv(temp_path, index=False)

print("\n🎉 SELESAI! YouTube berhasil disimpan.")
