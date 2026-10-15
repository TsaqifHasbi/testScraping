import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

print("=" * 65)
print("SIMULASI FILTER THREADS SESUAI PERMINTAAN USER")
print("=" * 65)

# Load current Threads dataset (219,606 rows without Meta AI bot)
input_path = 'ScrapeData/scraped_Threads_Only.csv'
df = pd.read_csv(input_path, low_memory=False)
total_input = len(df)
print(f"Total data input: {total_input:,} baris")

# 1. Deteksi Reply / Membalas
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.IGNORECASE
)
content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(reply_pat)
print(f"\n1. Identifikasi Reply / Membalas:")
print(f"   - Total Postingan Balasan (Reply) : {is_reply.sum():,} baris (AKAN DIBUANG)")
print(f"   - Total Postingan Utama (Bukan)   : {(~is_reply).sum():,} baris (KANDIDAT DISIMPAN)")

# 2. Pola Relevansi Topik + Kata Sarkas/Sindiran MBG
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

print(f"\n2. Klasifikasi Konten:")
# Kategori 1: Postingan Utama Relevan (Termasuk Sarkasme/Sindiran MBG)
cat_keep = (~is_reply) & (has_topic_kw)
# Kategori 2: Reply / Balasan (Dibuang sesuai instruksi user)
cat_reply = is_reply
# Kategori 3: Algoritmik Nyasar (Non-reply tapi tanpa konteks topik)
cat_junk = (~is_reply) & (~has_topic_kw)

print(f"   - [DISIMPAN KE DATASET UTAMA] Postingan Utama Relevan (+ Sarkasme MBG) : {cat_keep.sum():,} baris")
print(f"   - [DIBUANG] Reply / Membalas (Kehilangan konteks diskusi)             : {cat_reply.sum():,} baris")
print(f"   - [DIBUANG] Algoritmik Nyasar / Spam (Jual mobil, loker, tips hp dll) : {cat_junk.sum():,} baris")
print(f"   - Total Data yang Dibuang                                             : {(cat_reply.sum() + cat_junk.sum()):,} baris")

# Check breakdown of kept posts by topic
print("\n3. Rincian Postingan Utama yang Disimpan per Topik:")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    sub_count = ((df['topic'] == t) & cat_keep).sum()
    print(f"   - {t:15}: {sub_count:,} baris")
