import os
import sys
import io
import pandas as pd

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ORIGINAL_BACKUP = 'ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv'
TARGET_THREADS = 'ScrapeData/scraped_Threads_Only.csv'
DELETED_META_LOG = 'ScrapeData/scraped_Threads_Meta_AI_Dihapus.csv'

print("=" * 65)
print("🔄 MERESTORE DATASET AWAL THREADS (HANYA MENGHAPUS BOT RESMI @META.AI)")
print("=" * 65)

if not os.path.exists(ORIGINAL_BACKUP):
    print(f"❌ Error: File backup awal tidak ditemukan di {ORIGINAL_BACKUP}")
    sys.exit(1)

# 1. Buka dataset awal lengkap sebelum filter apapun
df_raw = pd.read_csv(ORIGINAL_BACKUP, low_memory=False)
total_raw = len(df_raw)
print(f"Loaded raw dataset: {total_raw:,} baris")

# 2. Identifikasi Postingan / Jawaban Bot Resmi Meta AI (@meta.ai)
is_meta_author = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)

# Identifikasi postingan netizen yang ngetag / memanggil meta.ai dalam isi kontennya
is_tagging_meta = df_raw['content'].fillna('').astype(str).str.contains(r'\bmeta\.?ai\b', case=False, regex=True) & (~is_meta_author)

count_meta_author = is_meta_author.sum()
count_tagging = is_tagging_meta.sum()

print(f"\n📊 Rincian Data:")
print(f"  - Total Data Mentah Awal         : {total_raw:,} baris")
print(f"  - Postingan dari Bot @meta.ai    : {count_meta_author:,} baris (DIBUANG)")
print(f"  - Postingan User Ngetag Meta AI  : {count_tagging:,} baris (DIKEMBALIKAN / DISIMPAN)")
print(f"  - Postingan User Lainnya         : {(total_raw - count_meta_author - count_tagging):,} baris (DISIMPAN)")

# 3. Pisahkan dataset:
# df_restored: Semua data awal KECUALI yang dibuat oleh bot @meta.ai
df_restored = df_raw[~is_meta_author].copy()
# df_deleted_meta: Hanya postingan resmi dari bot @meta.ai
df_deleted_meta = df_raw[is_meta_author].copy()
df_deleted_meta['keterangan_hapus'] = 'Postingan / Jawaban Bot Resmi Meta AI (@meta.ai)'

total_restored = len(df_restored)
print(f"\n✅ Total Data Akhir di {TARGET_THREADS}: {total_restored:,} baris")

# 4. Simpan file
df_restored.to_csv(TARGET_THREADS, index=False, encoding='utf-8')
print(f"💾 Berhasil menyimpan data terestorasi ke {TARGET_THREADS}")

df_deleted_meta.to_csv(DELETED_META_LOG, index=False, encoding='utf-8')
print(f"💾 Berhasil memperbarui log data Meta AI yang dihapus ke {DELETED_META_LOG} ({len(df_deleted_meta):,} baris)")

print("\n" + "=" * 65)
print("🎉 RESTORASI SELESAI DENGAN SUKSES!")
print("=" * 65)
