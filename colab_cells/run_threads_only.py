import os
import sys
import time
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_08_threads import scrape_threads, load_seen_urls, reset_tracking

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

print("=" * 60)
print("🚀 MEMULAI SCRAPING THREADS (FULL CRAWL)")
print("📅 Strategi: Ambil SEMUA data dari 1 Januari 2025 - Sekarang")
print("🔍 Tab: Recent (kronologis, hasil lebih relevan)")
print("🔄 Auto-Resume: Ya")
print("=" * 60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

temp_path = os.path.join(OUTPUT_DIR, "scraped_Threads_Only.csv")
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

print()
print("=" * 60)
print("[OK] KONFIGURASI SELESAI")
print(f"[INFO] Topik: {len(TOPICS)} topik")
print(f"[INFO] Keywords: {total_keywords} variasi keyword")
print("[INFO] Target: Semua data dari 1 Jan 2025 (batas tanggal, bukan angka)")
print("=" * 60)

for topic, keywords in TOPICS.items():
    print(f"\n[TOPIK] {topic}: {len(keywords)} keywords")
    for kw in keywords[:5]:
        print(f"   - {kw}")
    if len(keywords) > 5:
        print(f"   - ... dan {len(keywords) - 5} lainnya")

print()

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
            # Target sangat tinggi — biarkan tanggal cutoff (1 Jan 2025) yang jadi pembatas
            # Script akan scroll terus di tab Recent sampai post-nya melewati 1 Jan 2025
            target_results = 10000
            data = scrape_threads(kw, max_results=target_results)

            for d in data:
                d['topic'] = topic

            all_results.extend(data)

            # SIMPAN LANGSUNG + DEDUPLIKASI by URL
            df_temp = pd.DataFrame(all_results)
            if 'url' in df_temp.columns:
                before = len(df_temp)
                # Hanya dedup baris yang punya URL (bukan kosong)
                mask_has_url = df_temp['url'].notna() & (df_temp['url'] != '')
                df_with_url = df_temp[mask_has_url].drop_duplicates(subset=['url'], keep='first')
                df_no_url = df_temp[~mask_has_url]
                df_temp = pd.concat([df_with_url, df_no_url], ignore_index=True)
                removed = before - len(df_temp)
                if removed > 0:
                    print(f"  [DEDUP] Dihapus {removed} duplikat URL.")
                    all_results = df_temp.to_dict('records')

            df_temp.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [OK] Tersimpan! Total data di CSV: {len(df_temp)}")

        except KeyboardInterrupt:
            print("\n\n  [!] DIHENTIKAN OLEH USER — menyimpan data yang sudah terkumpul...")
            df_save = pd.DataFrame(all_results)
            if 'url' in df_save.columns and len(df_save) > 0:
                df_save.drop_duplicates(subset=['url'], inplace=True)
            df_save.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [OK] {len(df_save)} data tersimpan ke {temp_path}")
            print("  [INFO] Jalankan ulang script ini untuk melanjutkan (auto-resume).")
            sys.exit(0)

        except Exception as e:
            print(f"  [ERROR] Scraping gagal pada keyword '{kw}': {e}")
            # Simpan data yang sudah ada dulu
            if all_results:
                df_save = pd.DataFrame(all_results)
                df_save.to_csv(temp_path, index=False, encoding='utf-8-sig')
                print(f"  [SAVE] Data tersimpan ({len(df_save)} baris) sebelum restart.")
            
            print("  [INFO] Merestart Chrome untuk keyword berikutnya...")
            import cell_08_threads
            if cell_08_threads.THREADS_DRIVER is not None:
                try:
                    cell_08_threads.THREADS_DRIVER.quit()
                except Exception:
                    pass
            cell_08_threads.THREADS_DRIVER = None
            cell_08_threads._kill_zombie_chrome()
            time.sleep(3)

        current_kw += 1

# Final dedup & save
df_final = pd.DataFrame(all_results)
if 'url' in df_final.columns and len(df_final) > 0:
    mask_has_url = df_final['url'].notna() & (df_final['url'] != '')
    df_with_url = df_final[mask_has_url].drop_duplicates(subset=['url'], keep='first')
    df_no_url = df_final[~mask_has_url]
    df_final = pd.concat([df_with_url, df_no_url], ignore_index=True)
df_final.to_csv(temp_path, index=False, encoding='utf-8-sig')

print("\n" + "=" * 60)
print("🎉 SELESAI! Scraping Threads berhasil.")
print(f"📊 Total data final: {len(df_final)} baris")
print(f"📁 Tersimpan di: {temp_path}")
print("=" * 60)
