import os
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_05_tiktok import scrape_tiktok

print("="*60)
print("[START] MEMULAI SCRAPING TIKTOK ONLY")
print("="*60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

for topic, keywords in TOPICS.items():
    print(f"\n[{topic}] Memproses {len(keywords)} keyword...")
    
    for kw in keywords:
        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}'")
        
        # Jalankan Selenium TikTok untuk keyword ini
        # Set max_results sesuai kebutuhan (misal 50 atau 100)
        data = scrape_tiktok(kw, max_results=50)
        
        # Tambahkan label topic ke data
        for d in data:
            d['topic'] = topic
            
        all_results.extend(data)
        current_kw += 1

        # Buat dataframe dan hapus data duplikat (video yang sama muncul di keyword berbeda)
        df_temp = pd.DataFrame(all_results)
        df_temp.drop_duplicates(subset=['url'], inplace=True)
        
        # Simpan sementara (Auto-save)
        temp_path = os.path.join(OUTPUT_DIR, "scraped_TikTok_Only.csv")
        df_temp.to_csv(temp_path, index=False)

print("\n" + "="*60)
print(f"🎉 SELESAI! Total {len(all_results)} data TikTok berhasil disimpan ke:")
print(temp_path)
print("="*60)
