import os
import sys
import io
import pandas as pd
import re

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

ORIGINAL_BACKUP = 'ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv'
MAIN_CSV = 'ScrapeData/scraped_Threads_Only.csv'
CANDIDATE_CSV = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'

print("=" * 80)
print("🚀 MASTER THREADS FILTER: DARI RAW BEFORE_FILTER (ALL TOPICS + ANTI-REPLY)")
print("=" * 80)

print(f"Membaca file sumber mentah: {ORIGINAL_BACKUP}...")
df_raw = pd.read_csv(ORIGINAL_BACKUP, low_memory=False)
total_raw = len(df_raw)
print(f"Total baris awal di BEFORE_FILTER: {total_raw:,} baris")

# 1. Singkirkan bot resmi Meta AI
is_meta = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)
df = df_raw[~is_meta].copy().reset_index(drop=True)
print(f"Total baris setelah hapus bot Meta AI: {len(df):,} baris")

content = df['content'].fillna('').astype(str)

# 2. Deteksi Ketat Reply / Balasan (Wajib Dibuang)
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.I
)
is_reply = content.str.contains(reply_pat)
print(f"Postingan Balasan / Reply (Membalas @) : {is_reply.sum():,} baris (DIBUANG)")
print(f"Postingan Utama (Top-level Post)       : {(~is_reply).sum():,} baris (DIPERIKSA KELAYAKAN)")

# 3. KAMUS POLA TIAP TOPIK (CORE ANCHOR + CONTEXTUAL CO-OCCURRENCE)

# --- A. TOPIK 1: MBG (Makan Bergizi Gratis) ---
pat_mbg_core = re.compile(
    r'\bmbg\b|'
    r'makan(?:an)?\s+bergizi\s+gratis|'
    r'makan(?:an)?\s+gratis\s+bergizi|'
    r'makan\s+siang\s+gratis|'
    r'makan\s+gratis\s+siang|'
    r'makan\s+bergizi\s+gak\s+gratis|makan\s+bergizi\s+tentunya\s+tidak\s+gratis|'
    r'badan\s+gizi\s+nasional|\bbgn\b|'
    r'dadan\s+hindayana|\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
    r'dapur\s+(?:gizi|mbg|sehat|komunal)|'
    r'murderer\s+by\s+government|badan\s+genosida\s+negara|'
    r'(?:prabowo|gibran).{0,35}(?:makan|gizi|susu|ompreng|bgn)',
    re.I
)

pat_mbg_cooccur = re.compile(
    # Keracunan / beracun berpasangan dengan sekolah/siswa/katering/uji coba/mbg
    r'(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun).{0,70}(?:siswa|murid|anak|sekolah|sd\b|smp\b|sma\b|santri|pesantren|program|gratis|uji\s*coba|massal|katering|dapur|vendor|ompreng|korban)|'
    r'(?:siswa|murid|anak|sekolah|santri|pesantren|warga|korban).{0,70}(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun)|'
    # Ompreng berkaitan dengan makanan/cuci/sekolah
    r'ompreng.{0,60}(?:makan|lauk|nasi|sayur|cuci|dapur|sekolah|anak|siswa|murid|guru|katering|program|sticker|stiker|relawan)|'
    r'(?:makan|cuci|wadah|tempat|piring|katering|dapur|guru|siswa|relawan).{0,60}ompreng|'
    # Susu program/ikan
    r'susu\s+ikan|'
    r'susu.{0,50}(?:mbg|bgn|gratis|program|sekolah|siswa|anak|murid|pengganti\s+susu|impor|peternak|sapi|lokal)|'
    # Menu 10rb / 15rb / anggaran
    r'(?:menu|porsi|anggaran|biaya|alokasi).{0,50}(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu|71\s*t|triliun|335\s*t|apbn|per\s+porsi|per\s+anak)|'
    r'(?:program|uji\s*coba|katering|vendor).{0,50}(?:10\s*rb|15\s*rb|porsi|nasi)|'
    # Makanan bergizi / makan siang berpasangan dengan kebijakan
    r'makan(?:an)?\s+bergizi.{0,50}(?:gratis|anak\s+sekolah|siswa|murid|santri|nasional|apbn|program\s+pemerintah|stunting)|'
    r'(?:program|proyek|kebijakan|janji|uji\s*coba|anggaran|subsidi)\s+(?:makan\s+siang|makan(?:an)?\s+bergizi|makan\s+gratis)|'
    r'makan\s+siang.{0,50}(?:gratis|sekolah|siswa|murid|anak\s+sd|anak\s+smp|presiden|pemerintah)|'
    # Makan gratis program/anak/sekolah
    r'(?:dikasih|bagi-bagi|program)\s+makan\s+gratis|'
    r'makan\s+gratis.{0,40}(?:anak|siswa|sekolah|stunting|rakyat|apbn)',
    re.I
)

# --- B. TOPIK 2: SEKOLAH RAKYAT ---
pat_sr_core = re.compile(
    r'sekolah\s+rakyat|'
    r'sekolah\s+gratis\s+rakyat|'
    r'sekolah\s+rakyat\s+gratis|'
    r'pendidikan\s+sekolah\s+rakyat|'
    r'sekolah\s+negeri\s+rakyat|'
    r'sekolah\s+rakyat\s+berasrama|'
    r'program\s+sekolah\s+rakyat',
    re.I
)

pat_sr_cooccur = re.compile(
    r'(?:sekolah|pendidikan)\s+gratis.{0,60}(?:rakyat|miskin|prabowo|gibran|pemerintah|program|asta\s*cita|asrama|daerah\s+terpencil|3t\b|anggaran|apbn)|'
    r'(?:prabowo|gibran|pemerintah).{0,60}(?:sekolah\s+gratis|sekolah\s+rakyat|pendidikan\s+gratis)|'
    r'kemendikdasmen|mendikdasmen|'
    r'sekolah\s+berasrama.{0,50}(?:gratis|rakyat|pemerintah|prabowo)|'
    r'dana\s+bos|bantuan\s+operasional\s+sekolah|'
    r'(?:biaya|uang)\s+(?:sekolah|spp|gedung|seragam).{0,40}(?:gratis|bebas|rakyat|pemerintah)|'
    r'(?:program|evaluasi|anggaran).{0,60}(?:sekolah|pendidikan|siswa|murid|guru\s+honorer)',
    re.I
)

# --- C. TOPIK 3: KDMP (Koperasi Desa Merah Putih) ---
pat_kdmp_core = re.compile(
    r'\bkdmp\b|\bkdkmp\b|\bknmp\b|agrinas|'
    r'koperasi\s+desa\s+merah\s+putih|'
    r'koperasi\s+merah\s+putih|'
    r'desa\s+merah\s+putih',
    re.I
)

pat_kdmp_cooccur = re.compile(
    r'koperasi\s+desa|kopdes|bumdes|'
    r'(?:koperasi|kopdes|bumdes).{0,60}(?:merah\s+putih|prabowo|program|pangan|distribusi|petani|nelayan|mbg|dana\s+desa|modal|umkm|bumn|himbara|kredit|sindikasi|plafon|triliun|miliar|manajer|rekrutmen|panselnas|phtc)|'
    r'(?:program|proyek|kebijakan).{0,60}(?:koperasi\s+desa|desa\s+mandiri\s+pangan|kdmp|kdkmp|kopdes)|'
    r'koperasi\s+umkm|'
    r'dana\s+desa.{0,50}(?:koperasi|bumdes|ketahanan\s+pangan)',
    re.I
)

# --- D. NEGATIVE NOISE EXCLUSIONS (Filter Sampah Lintas Topik) ---
pat_noise = re.compile(
    # Curhat Medis Kehamilan & Laktasi
    r'pejuang\s+garis\s+dua|promil|senam\s+hamil|yoga\s+hamil|'
    r'booster\s+asi|laktasi|asi\s+eksklusif|sufor|pompa\s+asi|kantung\s+asi|kantong\s+asi|'
    r'usg\s+(?:2d|3d|4d)|bbj\s+janin|periksa\s+kandungan|'
    r'beli\s+2\s+gratis\s+1|promo\s+diskon|beli\s+susu\s+di\s+(?:indomaret|alfamart)|'
    # Isu Malaysia / Jerebu
    r'kpm\s+dan\s+kkm|isu\s+jerebu|bakar\s+hutan\s+korang|menteri\s+malaysia|'
    # Isu Politik Nyasar tanpa sentuhan program
    r'ijazah\s+(?:jokowi|gibran)|fufufafa|maling\s+motor|kopassus|jis\s+dapat|ikn\s+mangkrak|'
    r'saham\s+bbca|laba\s+q1|'
    # Slang & topik lain
    r'naik\s+ompreng|mobil\s+ompreng|racun\s+shopee|racun\s+tiktok|'
    r'running\s+threads|lari\s+setiap\s+hari|yg\s+indigo|sk\s+pns\s+ku|freedive',
    re.I
)

# Evaluasi kecocokan per topik
match_mbg = content.str.contains(pat_mbg_core) | content.str.contains(pat_mbg_cooccur)
match_sr = content.str.contains(pat_sr_core) | content.str.contains(pat_sr_cooccur)
match_kdmp = content.str.contains(pat_kdmp_core) | content.str.contains(pat_kdmp_cooccur)

has_any_topic = match_mbg | match_sr | match_kdmp
hits_noise = content.str.contains(pat_noise)

has_strong_core = (
    content.str.contains(pat_mbg_core) |
    content.str.contains(pat_sr_core) |
    content.str.contains(pat_kdmp_core)
)

keep_mask = (~is_reply) & has_any_topic & (~hits_noise | has_strong_core)
discard_mask = ~keep_mask

# Rekonsiliasi Topik (Cross-topic alignment)
new_topic = df['topic'].copy()
# Jika topik awal KDMP / Sekolah Rakyat tapi isi konten murni MBG:
is_actually_mbg = (df['topic'] != 'MBG') & match_mbg & (~match_kdmp) & (~match_sr)
new_topic[is_actually_mbg] = 'MBG'

# Jika topik awal MBG tapi isi konten murni KDMP:
is_actually_kdmp = (df['topic'] == 'MBG') & match_kdmp & (~match_mbg)
new_topic[is_actually_kdmp] = 'KDMP'

# Jika topik awal MBG/KDMP tapi isi konten murni Sekolah Rakyat:
is_actually_sr = (df['topic'] != 'Sekolah_Rakyat') & match_sr & (~match_mbg) & (~match_kdmp)
new_topic[is_actually_sr] = 'Sekolah_Rakyat'

df['topic'] = new_topic

df_clean = df[keep_mask].copy()
df_discarded = df[discard_mask].copy()

# Buat alasan penghapusan yang transparan
reasons = []
for idx in df_discarded.index:
    if is_reply[idx]:
        reasons.append('Postingan Balasan / Reply (Membalas @... / kehilangan konteks)')
    elif hits_noise[idx]:
        reasons.append('Kategori Noise Terdeteksi (Curhat Hamil/Laktasi/Ijazah/Jerebu/Promo Komersial)')
    else:
        reasons.append('Rekomendasi Algoritmik / Konten Nyasar (Tanpa kata kunci & sentimen topik)')

df_discarded['alasan_rekomendasi_hapus'] = reasons

print("\n" + "=" * 80)
print("HASIL PEMROSESAN MASTER FILTER:")
print("=" * 80)
print(f"Total Baris Mentah (Raw)      : {total_raw:,} baris")
print(f"Total Bot Meta AI Dihapus     : {is_meta.sum():,} baris")
print(f"Total Baris Diproses          : {len(df):,} baris")
print(f"✅ Disimpan ke Dataset Utama  : {len(df_clean):,} baris ({len(df_clean)/len(df)*100:.1f}%)")
print(f"❌ Dibuang ke Kandidat Hapus  : {len(df_discarded):,} baris ({len(df_discarded)/len(df)*100:.1f}%)")
print(f"   - Postingan Balasan (Reply): {is_reply.sum():,} baris")
print(f"   - Noise / Konten Nyasar    : {(discard_mask & ~is_reply).sum():,} baris")

print("\n📈 Distribusi Dataset Bersih per Topik:")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    cnt = (df_clean['topic'] == t).sum()
    print(f"   - {t:15}: {cnt:,} baris")

print("\n📉 Rincian Alasan pada File Kandidat Hapus:")
print(df_discarded['alasan_rekomendasi_hapus'].value_counts())

# Simpan ke CSV
cols_original = ['platform', 'keyword', 'url', 'handle', 'content', 'created_at', 'likes', 'comments', 'reposts', 'shares', 'views', 'scraped_at', 'topic']
df_clean = df_clean[cols_original]
df_clean.to_csv(MAIN_CSV, index=False, encoding='utf-8')
print(f"\n💾 Berhasil menyimpan {MAIN_CSV} ({len(df_clean):,} baris)")

df_discarded.to_csv(CANDIDATE_CSV, index=False, encoding='utf-8')
print(f"💾 Berhasil menyimpan {CANDIDATE_CSV} ({len(df_discarded):,} baris)")
print("=" * 80)
