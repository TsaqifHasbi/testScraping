import sys
import io
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

ORIGINAL_BACKUP = 'ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv'
CANDIDATE_CSV = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'

print("Loading raw data from BEFORE_FILTER...")
df_raw = pd.read_csv(ORIGINAL_BACKUP, low_memory=False)

# Identify Meta AI bot rows
is_meta = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)

df_meta = df_raw[is_meta].copy()
df_meta['alasan_rekomendasi_hapus'] = 'Akun Resmi Bot Meta AI (@meta.ai)'
print(f"Total baris bot Meta AI: {len(df_meta):,} baris")

print(f"Loading current {CANDIDATE_CSV}...")
df_kand = pd.read_csv(CANDIDATE_CSV, low_memory=False)
print(f"Total baris Kandidat Hapus sebelumnya: {len(df_kand):,} baris")

# Gabungkan Meta AI ke Kandidat Hapus
df_kand_merged = pd.concat([df_kand, df_meta], ignore_index=True)
print(f"Total baris Kandidat Hapus setelah digabung: {len(df_kand_merged):,} baris")

print("\nRincian Alasan pada File Kandidat Hapus Sekarang:")
print(df_kand_merged['alasan_rekomendasi_hapus'].value_counts())

# Simpan kembali
df_kand_merged.to_csv(CANDIDATE_CSV, index=False, encoding='utf-8')
print(f"\n💾 Berhasil menyimpan {CANDIDATE_CSV} ({len(df_kand_merged):,} baris)")
