import os
import sys
import io
import pandas as pd
import re

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

THREADS_PATH = 'ScrapeData/scraped_Threads_Only.csv'
KANDIDAT_PATH = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'
DELETED_LOG_PATH = 'ScrapeData/scraped_Threads_Meta_AI_Dihapus.csv'

print("=" * 60)
print("🧹 MEMULAI PROSES FILTERING & PENGHAPUSAN META AI DARI THREADS")
print("=" * 60)

# 1. BACA DATASET UTAMA
df_main = pd.read_csv(THREADS_PATH, low_memory=False)
initial_len = len(df_main)
print(f"Total baris awal di {THREADS_PATH}: {initial_len:,}")

# Definisikan kriteria Meta AI
# - Postingan / balasan yang dibuat oleh akun Meta AI (@meta.ai)
is_meta_author = (
    df_main['handle'].astype(str).str.lower().str.strip() == '@meta.ai'
) | (
    df_main['url'].astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)

# - Prompt / interaksi panggilan ke bot Meta AI
is_meta_prompt = df_main['content'].fillna('').astype(str).str.contains(r'\bmeta\.?ai\b', case=False, regex=True)

# Gabungan seluruh baris terkait Meta AI
is_meta_any = is_meta_author | is_meta_prompt

df_deleted_meta = df_main[is_meta_any].copy()
df_clean_main = df_main[~is_meta_any].copy()

# Berikan keterangan kategori penghapusan
reasons = []
for idx in df_deleted_meta.index:
    if is_meta_author[idx]:
        reasons.append('Postingan / Jawaban Bot Resmi Meta AI (@meta.ai)')
    else:
        reasons.append('Prompt / Pertanyaan Netizen Memanggil Bot Meta AI')
df_deleted_meta['keterangan_hapus'] = reasons

print(f"\n📊 Rincian Data Meta AI yang Teridentifikasi:")
print(f"  - Postingan & Jawaban dari @meta.ai : {is_meta_author.sum():,}")
print(f"  - Prompt / Pemanggilan ke Meta AI  : {(is_meta_prompt & ~is_meta_author).sum():,}")
print(f"  - Total Data Meta AI Dihapus       : {len(df_deleted_meta):,}")
print(f"  - Sisa Data Bersih (Human Only)    : {len(df_clean_main):,}")

# Simpan log data yang dihapus ke file terpisah untuk transparansi
df_deleted_meta.to_csv(DELETED_LOG_PATH, index=False, encoding='utf-8')
print(f"\n💾 Berhasil mengekspor arsip data Meta AI yang dihapus ke: {DELETED_LOG_PATH}")

# Timpa dataset utama dengan versi bersih 100% tanpa Meta AI
df_clean_main.to_csv(THREADS_PATH, index=False, encoding='utf-8')
print(f"💾 Berhasil memperbarui {THREADS_PATH} (Sekarang bersih: {len(df_clean_main):,} baris)")

# 2. BERSIHKAN JUGA DARI KANDIDAT HAPUS JIKA ADA
if os.path.exists(KANDIDAT_PATH):
    df_kandidat = pd.read_csv(KANDIDAT_PATH, low_memory=False)
    len_kandidat_init = len(df_kandidat)
    
    k_meta_author = (
        df_kandidat['handle'].astype(str).str.lower().str.strip() == '@meta.ai'
    ) | (
        df_kandidat['url'].astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
    )
    k_meta_prompt = df_kandidat['content'].fillna('').astype(str).str.contains(r'\bmeta\.?ai\b', case=False, regex=True)
    k_meta_any = k_meta_author | k_meta_prompt
    
    df_clean_kandidat = df_kandidat[~k_meta_any].copy()
    df_clean_kandidat.to_csv(KANDIDAT_PATH, index=False, encoding='utf-8')
    print(f"\n💾 Berhasil membersihkan {KANDIDAT_PATH}:")
    print(f"  - Sebelum: {len_kandidat_init:,} baris")
    print(f"  - Dihapus: {k_meta_any.sum():,} baris Meta AI")
    print(f"  - Sesudah: {len(df_clean_kandidat):,} baris")

print("\n" + "=" * 60)
print("✅ SEMUA DATA POSTINGAN & JAWABAN META AI SUDAH DIBERSIHKAN DENGAN SEMPURNA!")
print("=" * 60)
