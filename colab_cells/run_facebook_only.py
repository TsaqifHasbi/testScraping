import os
import sys

# Fix Windows console encoding SEBELUM import apapun (cell_02_config mencetak emoji)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

import time
import pandas as pd
from cell_02_config import TOPICS, OUTPUT_DIR
from cell_09_facebook import scrape_facebook, load_seen_urls, reset_tracking, _force_relogin, FB_PROFILE_DIR

# OPSI FRESH LOGIN / RELOGIN VIA ARGUMENT
if '--relogin' in sys.argv or '--fresh-login' in sys.argv:
    print("[INFO] Parameter --relogin terdeteksi: mereset session untuk login akun baru...")
    _force_relogin()

print("=" * 60)
print("🚀 MEMULAI SCRAPING FACEBOOK ONLY")
print("📊 Target Quota:")
print("   - 2 Keyword Utama per Topik : 1000 data")
print("   - Keyword Sisanya           : 100 data")
print("🔄 Auto-Resume: Aktif (skip keyword yang sudah selesai)")
print("💾 Auto-Save  : Langsung tersimpan ke CSV setiap 1 keyword selesai")
print("=" * 60)

all_results = []
total_keywords = sum(len(kws) for kws in TOPICS.values())
current_kw = 1

temp_path = os.path.join(OUTPUT_DIR, "scraped_Facebook_Only.csv")
existing_keywords = set()

# OPSI FRESH START / RE-SCRAPE VIA ARGUMENT
is_fresh = '--fresh' in sys.argv or '--reset' in sys.argv

# AUTO-RESUME vs FRESH START: Cek CSV yang sudah ada
if os.path.exists(temp_path) and not is_fresh:
    try:
        try:
            df_existing = pd.read_csv(temp_path, encoding='utf-8-sig')
        except Exception:
            df_existing = pd.read_csv(temp_path)

        if 'keyword' in df_existing.columns:
            existing_keywords = set(df_existing['keyword'].dropna().unique())
        all_results = df_existing.to_dict('records')

        # Load existing URLs untuk deduplikasi global
        if 'url' in df_existing.columns:
            existing_urls = set(df_existing['url'].dropna().unique())
            load_seen_urls(existing_urls)

        print(f"[INFO] Melanjutkan dari file yang ada!")
        print(f"       - {len(existing_keywords)} keyword sudah selesai di-scrape")
        print(f"       - {len(all_results)} data sudah tersimpan di CSV")
        print(f"       (Gunakan flag --fresh jika ingin mengulang scraping dari awal)")
    except Exception as e:
        print(f"[WARN] Gagal membaca CSV lama: {e}")
        reset_tracking()
else:
    if is_fresh and os.path.exists(temp_path):
        import shutil
        backup_p = os.path.join(OUTPUT_DIR, "scraped_Facebook_Only_BACKUP.csv")
        try:
            shutil.copy2(temp_path, backup_p)
            print(f"[BACKUP] File CSV lama diamankan ke {backup_p}")
        except Exception as e:
            print(f"[WARN] Gagal backup: {e}")
        print("[RESET] Memulai scraping Facebook dari awal (Fresh Start)...")
    reset_tracking()

print()
print("=" * 60)
print("[OK] KONFIGURASI SELESAI")
print(f"[INFO] Topik: {len(TOPICS)} topik")
print(f"[INFO] Keywords: {total_keywords} total variasi keyword")
print("=" * 60)

for topic, keywords in TOPICS.items():
    print(f"\n{'=' * 40}")
    print(f"[{topic}] Memproses {len(keywords)} keyword...")
    print(f"{'=' * 40}")

    for i, kw in enumerate(keywords):
        # 2 keyword utama ambil 1000 data, sisanya 100 data
        target_results = 1000 if i < 2 else 100

        print(f"\n  [{current_kw}/{total_keywords}] Keyword: '{kw}' (Target: {target_results} data)")

        # SMART QUOTA REFILL: Cek berapa data yang sudah ada di CSV untuk keyword ini
        current_count = 0
        if len(all_results) > 0:
            current_count = sum(1 for r in all_results if r.get('keyword') == kw)

        if current_count >= target_results:
            print(f"  [SKIP] Keyword '{kw}' sudah memenuhi target ({current_count}/{target_results} data).")
            current_kw += 1
            continue

        needed = target_results - current_count
        if current_count > 0:
            print(f"  [REFILL] Keyword '{kw}' baru ada {current_count}/{target_results} data. Melanjutkan ambil {needed} data lagi...")
        else:
            print(f"  [START] Keyword '{kw}' belum ada di CSV. Mengambil target {needed} data...")

        try:
            data = scrape_facebook(kw, max_results=needed)

            for d in data:
                d['topic'] = topic

            all_results.extend(data)

            # SIMPAN LANGSUNG + DEDUPLIKASI by URL
            df_temp = pd.DataFrame(all_results)
            if 'url' in df_temp.columns and len(df_temp) > 0:
                before = len(df_temp)
                mask_has_url = df_temp['url'].notna() & (df_temp['url'] != '')
                df_with_url = df_temp[mask_has_url].drop_duplicates(subset=['url'], keep='first')
                df_no_url = df_temp[~mask_has_url]
                df_temp = pd.concat([df_with_url, df_no_url], ignore_index=True)
                removed = before - len(df_temp)
                if removed > 0:
                    print(f"  [DEDUP] Dihapus {removed} duplikat URL.")
                    all_results = df_temp.to_dict('records')

            # Standarisasi urutan kolom
            cols_order = ['platform', 'topic', 'content', 'author', 'url', 'likes', 'comments', 'shares', 'keyword', 'scraped_at']
            ordered = [c for c in cols_order if c in df_temp.columns] + [c for c in df_temp.columns if c not in cols_order]
            df_temp = df_temp[ordered]

            df_temp.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [OK] Tersimpan! Total data di CSV: {len(df_temp)}")

        except KeyboardInterrupt:
            print("\n\n  [!] DIHENTIKAN OLEH USER (Ctrl+C) — menyimpan data yang sudah terkumpul...")
            df_save = pd.DataFrame(all_results)
            if 'url' in df_save.columns and len(df_save) > 0:
                mask_has_url = df_save['url'].notna() & (df_save['url'] != '')
                df_with_url = df_save[mask_has_url].drop_duplicates(subset=['url'], keep='first')
                df_no_url = df_save[~mask_has_url]
                df_save = pd.concat([df_with_url, df_no_url], ignore_index=True)
            cols_order = ['platform', 'topic', 'content', 'author', 'url', 'likes', 'comments', 'shares', 'keyword', 'scraped_at']
            ordered = [c for c in cols_order if c in df_save.columns] + [c for c in df_save.columns if c not in cols_order]
            df_save = df_save[ordered]
            df_save.to_csv(temp_path, index=False, encoding='utf-8-sig')
            print(f"  [OK] {len(df_save)} data tersimpan ke {temp_path}")
            print("  [INFO] Jalankan ulang script ini kapan saja untuk melanjutkan (auto-resume).")
            sys.exit(0)

        except Exception as e:
            print(f"  [ERROR] Scraping gagal/terputus pada keyword '{kw}': {e}")
            if all_results:
                df_save = pd.DataFrame(all_results)
                df_save.to_csv(temp_path, index=False, encoding='utf-8-sig')
                print(f"  [SAVE] Data tersimpan ({len(df_save)} baris) sebelum recovery.")

            print("  [INFO] Merestart Chrome untuk keyword berikutnya...")
            import cell_09_facebook
            try:
                if cell_09_facebook.FB_DRIVER is not None:
                    cell_09_facebook.FB_DRIVER.quit()
            except Exception:
                pass
            cell_09_facebook.FB_DRIVER = None
            time.sleep(3)

        current_kw += 1

# Final dedup & save
df_final = pd.DataFrame(all_results)
if 'url' in df_final.columns and len(df_final) > 0:
    mask_has_url = df_final['url'].notna() & (df_final['url'] != '')
    df_with_url = df_final[mask_has_url].drop_duplicates(subset=['url'], keep='first')
    df_no_url = df_final[~mask_has_url]
    df_final = pd.concat([df_with_url, df_no_url], ignore_index=True)

cols_order = ['platform', 'topic', 'content', 'author', 'url', 'likes', 'comments', 'shares', 'keyword', 'scraped_at']
ordered = [c for c in cols_order if c in df_final.columns] + [c for c in df_final.columns if c not in cols_order]
df_final = df_final[ordered]
df_final.to_csv(temp_path, index=False, encoding='utf-8-sig')

print("\n" + "=" * 60)
print(f"🎉 SELESAI! Total {len(df_final)} data Facebook unik berhasil disimpan ke:")
print(temp_path)
if 'topic' in df_final.columns and len(df_final) > 0:
    print(f"\nDistribusi topik:")
    print(df_final['topic'].value_counts().to_string())
print("=" * 60)
