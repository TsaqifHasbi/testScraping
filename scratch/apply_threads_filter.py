import os
import sys
import io
import pandas as pd
import re

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MAIN_CSV = 'ScrapeData/scraped_Threads_Only.csv'
CANDIDATE_CSV = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'

print("=" * 70)
print("🚀 MEMPROSES PEMISAHAN & PENYELAMATAN KONTEN SARKASME MBG DI THREADS")
print("=" * 70)

# Load data
df = pd.read_csv(MAIN_CSV, low_memory=False)
total_awal = len(df)
print(f"📁 Memuat dataset Threads: {total_awal:,} baris")

# 1. Deteksi Pola Balasan / Reply (Membalas @, Replying to @, Balasan pada postingan, dll.)
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.IGNORECASE
)
content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(reply_pat)
print(f"\n1. Analisis Pola Diskusi:")
print(f"   - Postingan Balasan (Reply / Membalas) : {is_reply.sum():,} baris")
print(f"   - Postingan Utama (Bukan Reply)        : {(~is_reply).sum():,} baris")

# 2. Pola Relevansi Topik + Kata Sarkas/Sindiran MBG Lengkap
PATTERNS = {
    'MBG': re.compile(
        r'(?:'
        # Sarkasme & Sindiran MBG (sesuai instruksi user)
        r'makan(?:an)?\s+beracun(?:\s+gratis)?|'
        r'makan(?:an)?\s+gratis\s+beracun|'
        r'makan(?:an)?\s+basi(?:\s+gratis)?|'
        r'makan(?:an)?\s+gratis\s+basi|'
        r'makan\s+siang\s+beracun|'
        r'bagi(?:-bagi)?\s+racun|'
        r'ompreng(?:an)?|'
        r'susu\s+(?:basi|ikan|gratis|uht)|'
        r'janji\s+(?:manis\s+)?makan|'
        r'menu\s+(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu)|'
        r'(?:korban|kasus|dugaan|insiden)?\s*(?:keracunan|beracun).{0,50}(?:makan|siswa|murid|anak|sekolah|massal|program|gratis|uji\s*coba)|'
        r'(?:siswa|murid|anak|sekolah).{0,50}(?:keracunan|beracun)|'
        # Istilah Resmi & Variasi MBG
        r'makanan\s+bergizi\s+gratis|'
        r'makan(?:an)?\s+gratis\s+bergizi|'
        r'makan(?:an)?.{0,20}bergizi|'
        r'makan(?:an)?.{0,20}gratis|'
        r'makan(?:an)?.{0,20}siang|'
        r'\bmbg\b|'
        r'badan\s+gizi\s+nasional|\bbgn\b|'
        r'dadan\s+hindayana|'
        r'\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
        r'dapur\s+(?:gizi|mbg|sehat|komunal|umum)|'
        r'menu\s+mbg|anggaran\s+(?:mbg|makan|gizi)|'
        r'program\s+makan(?:an)?|'
        r'proyek\s+makan(?:an)?|'
        r'uji\s+coba\s+makan|'
        r'vendor\s+makan|katering\s+makan|'
        r'gizi.{0,25}(?:anak|siswa|murid|sekolah|bumil|ibu|hamil)|'
        r'(?:prabowo|gibran).{0,40}(?:makan|gizi|susu)'
        r')',
        re.IGNORECASE
    ),
    'KDMP': re.compile(
        r'(?:'
        r'\bkdmp\b|koperasi\s+desa|desa\s+merah\s+putih|koperasi\s+merah\s+putih|'
        r'desa\s+mandiri\s+pangan|\bkoperasi\b|dana\s+desa|kopdes|bumdes|'
        r'koperasi\s+umkm'
        r')',
        re.IGNORECASE
    ),
    'Sekolah_Rakyat': re.compile(
        r'(?:'
        r'sekolah\s+rakyat|sekolah\s+gratis\s+rakyat|sekolah.{0,20}gratis|'
        r'pendidikan\s+sekolah\s+rakyat|pendidikan.{0,20}rakyat|'
        r'kemendikdasmen|sekolah\s+negeri\s+rakyat'
        r')',
        re.IGNORECASE
    )
}

has_topic_kw = pd.Series(False, index=df.index)
for t, pat in PATTERNS.items():
    mask = (df['topic'] == t)
    has_topic_kw[mask] = content_str[mask].str.contains(pat)

# 3. Klasifikasi Data
# A. Postingan Utama Relevan (Termasuk Sarkasme/Sindiran MBG) -> DISIMPAN
keep_mask = (~is_reply) & (has_topic_kw)

# B. Dibuang -> Reply atau Algoritmik Nyasar
discard_mask = ~keep_mask

df_clean = df[keep_mask].copy()

df_discarded = df[discard_mask].copy()
reasons = []
for idx in df_discarded.index:
    if is_reply[idx]:
        reasons.append('Postingan Balasan / Reply (Membalas @... / kehilangan konteks)')
    else:
        reasons.append('Rekomendasi Algoritmik / Konten Nyasar (Tanpa kata kunci & sentimen topik)')
df_discarded['alasan_rekomendasi_hapus'] = reasons

print(f"\n2. Hasil Klasifikasi:")
print(f"   ✅ Disimpan ke Dataset Utama ({MAIN_CSV}) : {len(df_clean):,} baris")
print(f"   ❌ Dibuang ke File Kandidat Hapus ({CANDIDATE_CSV}) : {len(df_discarded):,} baris")
print(f"      - Kategori Reply / Membalas            : {is_reply.sum():,} baris")
print(f"      - Kategori Algoritmik Nyasar (Spam)    : {(discard_mask & ~is_reply).sum():,} baris")

print("\n3. Rincian Dataset Utama per Topik:")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    cnt = (df_clean['topic'] == t).sum()
    print(f"   - {t:15}: {cnt:,} baris")

# 4. Simpan File
# Simpan dataset utama yang sudah bersih dan bebas reply
cols_original = ['platform', 'keyword', 'url', 'handle', 'content', 'created_at', 'likes', 'comments', 'reposts', 'shares', 'views', 'scraped_at', 'topic']
df_clean = df_clean[cols_original]
df_clean.to_csv(MAIN_CSV, index=False, encoding='utf-8')
print(f"\n💾 Dataset utama berhasil diperbarui: {MAIN_CSV} ({len(df_clean):,} baris)")

# Simpan kandidat hapus terupdate
df_discarded.to_csv(CANDIDATE_CSV, index=False, encoding='utf-8')
print(f"💾 File log data dibuang berhasil diperbarui: {CANDIDATE_CSV} ({len(df_discarded):,} baris)")

print("\n" + "=" * 70)
print("🎉 PROSES FILTER SELESAI DENGAN SUKSES!")
print("=" * 70)
