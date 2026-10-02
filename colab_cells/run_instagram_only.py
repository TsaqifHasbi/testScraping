import os
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_07_instagram import scrape_instagram

print("="*60)
print("🚀 MEMULAI SCRAPING INSTAGRAM ONLY")
print("="*60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")
    
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        
        # Max results 30
        data = scrape_instagram(kw, max_results=30)
        
        for d in data:
            d['topic'] = topic
            
        all_results.extend(data)
        current_kw += 1

        df_temp = pd.DataFrame(all_results)
        temp_path = os.path.join(OUTPUT_DIR, "scraped_Instagram_Only.csv")
        df_temp.to_csv(temp_path, index=False)

print("\n" + "="*60)
print(f"🎉 SELESAI! Total {len(all_results)} data Instagram berhasil disimpan ke:")
print(temp_path)
print("="*60)
