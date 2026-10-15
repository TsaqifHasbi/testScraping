import os
import sys
import io
import pandas as pd
import re

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ORIGINAL_BACKUP = 'ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv'
MAIN_CSV = 'ScrapeData/scraped_Threads_Only.csv'
CANDIDATE_CSV = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'

print("=" * 75)
print("🚀 PEMBAHARUAN FILTER THREADS: MULTI-TOPIK, SARKASME LUAS & ANTI-REPLY")
print("=" * 75)

# Buka dari backup awal (bebas filter)
df_raw = pd.read_csv(ORIGINAL_BACKUP, low_memory=False)

# 1. Singkirkan bot resmi Meta AI
is_meta_author = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)
df = df_raw[~is_meta_author].copy()
print(f"Total data bersih dari bot Meta AI: {len(df):,} baris")

# 2. Deteksi Pola Balasan / Reply (Wajib dibuang sesuai instruksi)
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.IGNORECASE
)
content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(reply_pat)
print(f"Postingan Balasan / Reply : {is_reply.sum():,} baris (DIBUANG)")
print(f"Postingan Utama           : {(~is_reply).sum():,} baris (DIPERIKSA KELAYAKAN)")

# 3. Kamus Pola Lengkap (Fleksibel, Multi-Urutan, Sarkasme & Sentimen Kritis)
PATTERNS = {
    'MBG': re.compile(
        r'(?:'
        # Sarkasme & Sindiran MBG
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
        r'murderer\s+by\s+government|badan\s+genosida\s+negara|ternak\s+rakyat|'
        # Istilah Resmi, Variasi Kata Benda ("Makanan"), & Fleksibilitas Urutan
        r'makanan\s+bergizi\s+gratis|'
        r'makan(?:an)?\s+gratis\s+bergizi|'
        r'makan(?:an)?.{0,25}bergizi|'
        r'makan(?:an)?.{0,25}gratis|'
        r'makan(?:an)?.{0,25}siang|'
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

# Evaluasi kecocokan topik:
# 1. Cek kecocokan pada topik asalnya
match_mbg = content_str.str.contains(PATTERNS['MBG'])
match_kdmp = content_str.str.contains(PATTERNS['KDMP'])
match_sr = content_str.str.contains(PATTERNS['Sekolah_Rakyat'])

# Gabungan lintas topik (cross-topic): jika konten membahas MBG, KDMP, atau Sekolah Rakyat, konten ini RELEVAN!
has_any_topic = match_mbg | match_kdmp | match_sr

# Jika konten terdeteksi lebih dominan topik lain (misal di-scrape di KDMP tapi isinya murni MBG), sesuaikan topiknya
new_topic = df['topic'].copy()
# Jika topik awal KDMP/Sekolah Rakyat tapi kontennya jelas menyebut MBG/Makan Bergizi dan tidak menyebut koperasi/sekolah rakyat:
is_actually_mbg = (df['topic'] != 'MBG') & match_mbg & (~match_kdmp) & (~match_sr)
new_topic[is_actually_mbg] = 'MBG'

df['topic'] = new_topic

# 4. Klasifikasi Akhir
keep_mask = (~is_reply) & (has_any_topic)
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

print(f"\n📊 Hasil Pembaruan:")
print(f"   ✅ Disimpan ke Dataset Utama ({MAIN_CSV}) : {len(df_clean):,} baris")
print(f"   ❌ Dibuang ke File Kandidat Hapus ({CANDIDATE_CSV}) : {len(df_discarded):,} baris")
print(f"      - Kategori Reply / Membalas            : {is_reply.sum():,} baris")
print(f"      - Kategori Algoritmik Nyasar (Spam)    : {(discard_mask & ~is_reply).sum():,} baris")

print("\n📈 Rincian Dataset Utama per Topik:")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    cnt = (df_clean['topic'] == t).sum()
    print(f"   - {t:15}: {cnt:,} baris")

# 5. Simpan File
cols_original = ['platform', 'keyword', 'url', 'handle', 'content', 'created_at', 'likes', 'comments', 'reposts', 'shares', 'views', 'scraped_at', 'topic']
df_clean = df_clean[cols_original]
df_clean.to_csv(MAIN_CSV, index=False, encoding='utf-8')
print(f"\n💾 Berhasil memperbarui {MAIN_CSV} ({len(df_clean):,} baris)")

df_discarded.to_csv(CANDIDATE_CSV, index=False, encoding='utf-8')
print(f"💾 Berhasil memperbarui {CANDIDATE_CSV} ({len(df_discarded):,} baris)")

print("\n" + "=" * 75)
print("🎉 PEMBAHARUAN SELESAI!")
print("=" * 75)
