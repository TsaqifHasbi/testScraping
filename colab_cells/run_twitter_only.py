import os
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_04_twitter import scrape_twitter

print("="*60)
print("🚀 MEMULAI SCRAPING TWITTER (X) ONLY")
print("="*60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")
    
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        
        # Jalankan Selenium Twitter untuk keyword ini
        # Set max_results sesuai kebutuhan (misal 50 atau 100)
        data = scrape_twitter(kw, max_results=50)
        
        # Tambahkan label topic ke data
        for d in data:
            d['topic'] = topic
            
        all_results.extend(data)
        current_kw += 1

        # Simpan sementara (Auto-save) setiap selesai 1 keyword agar tidak hilang jika error
        df_temp = pd.DataFrame(all_results)
        df_temp.drop_duplicates(subset=['url'], inplace=True)
        
        temp_path = os.path.join(OUTPUT_DIR, "scraped_Twitter_Only.csv")
        df_temp.to_csv(temp_path, index=False)

print("\n" + "="*60)
print(f"🎉 SELESAI! Total {len(all_results)} data Twitter berhasil disimpan ke:")
print(temp_path)
print("="*60)
