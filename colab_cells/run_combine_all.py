import os
import pandas as pd
from cell_02_config import OUTPUT_DIR

print("="*60)
print("🚀 MENGGABUNGKAN SEMUA HASIL SCRAPING")
print("="*60)

# Cari semua file CSV yang namanya dimulai dari "scraped_" dan berakhiran "_Only.csv"
all_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("scraped_") and f.endswith("_Only.csv")]

if not all_files:
    print("Tidak ditemukan file CSV hasil scraping di folder ScrapeData.")
    exit()

dataframes = []
for file in all_files:
    path = os.path.join(OUTPUT_DIR, file)
    print(f"Membaca {file}...")
    try:
        df = pd.read_csv(path)
        dataframes.append(df)
    except Exception as e:
        print(f"Gagal membaca {file}: {e}")

# 1. Gabungkan Semua
combined_df = pd.concat(dataframes, ignore_index=True)
awal = len(combined_df)
print(f"\nTotal Data Keseluruhan (Mentah): {awal} baris")

# 2. Hapus Duplikat (Berdasarkan URL)
combined_df.drop_duplicates(subset=['url'], inplace=True)
akhir_url = len(combined_df)
print(f"Ditemukan {awal - akhir_url} duplikat URL. Sisa: {akhir_url} baris")

# 3. Hapus Baris yang Tidak Ada Content-nya
combined_df.dropna(subset=['content'], inplace=True)
akhir_content = len(combined_df)
print(f"Ditemukan {akhir_url - akhir_content} data tanpa teks konten. Sisa: {akhir_content} baris")

# 4. Simpan ke File Akhir (FINAL)
final_path = os.path.join(OUTPUT_DIR, "FINAL_ALL_DATA.csv")
combined_df.to_csv(final_path, index=False)

print("\n" + "="*60)
print(f"🎉 SUKSES! Data berhasil digabung dan dibersihkan.")
print(f"Total Data Bersih: {akhir_content} Baris")
print(f"Tersimpan di: {final_path}")
print("="*60)
