import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

ORIGINAL_BACKUP = 'ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv'

print("Loading raw data from BEFORE_FILTER...")
df_raw = pd.read_csv(ORIGINAL_BACKUP, low_memory=False)
print(f"Total raw rows: {len(df_raw):,}")

# 1. Bersihkan Akun Meta AI
is_meta = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)
df = df_raw[~is_meta].copy().reset_index(drop=True)
print(f"Rows after removing Meta AI bot: {len(df):,}")

content = df['content'].fillna('').astype(str)

# 2. Deteksi Ketat Reply / Balasan (Sesuai instruksi user: WAJIB DIBUANG)
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.I
)
is_reply = content.str.contains(reply_pat)
print(f"Replies / Balasan: {is_reply.sum():,} ({is_reply.sum()/len(df)*100:.1f}%) -> DIBUANG")
print(f"Top-level Postingan: {(~is_reply).sum():,} ({((~is_reply).sum())/len(df)*100:.1f}%) -> DIANALISIS")

# 3. KAMUS POLA LENGKAP TIAP TOPIK (Menggunakan Anchor + Co-occurrence Window)

# --- A. PATTERNS MBG ---
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

# Co-occurrence untuk sarkasme & kata ambigu MBG
pat_mbg_cooccur = re.compile(
    # Keracunan / beracun di sekolah/program/siswa
    r'(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun).{0,60}(?:siswa|murid|anak|sekolah|sd\b|smp\b|sma\b|santri|pesantren|program|gratis|uji\s*coba|massal|katering|dapur|vendor|ompreng|korban)|'
    r'(?:siswa|murid|anak|sekolah|santri|pesantren|warga|korban).{0,60}(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun)|'
    # Ompreng makanan/sekolah/cuci
    r'ompreng.{0,50}(?:makan|lauk|nasi|sayur|cuci|dapur|sekolah|anak|siswa|murid|guru|katering|program|sticker|stiker|relawan)|'
    r'(?:makan|cuci|wadah|tempat|piring|katering|dapur|guru|siswa|relawan).{0,50}ompreng|'
    # Susu program/sekolah/ikan
    r'susu\s+ikan|'
    r'susu.{0,40}(?:mbg|bgn|gratis|program|sekolah|siswa|anak|murid|pengganti\s+susu|impor|peternak|sapi|lokal)|'
    # Menu 10rb / 15rb / anggaran
    r'(?:menu|porsi|anggaran|biaya|alokasi).{0,40}(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu|71\s*t|triliun|335\s*t|apbn|per\s+porsi|per\s+anak)|'
    r'(?:program|uji\s*coba|katering|vendor).{0,40}(?:10\s*rb|15\s*rb|porsi|nasi)|'
    # Makanan bergizi / makan siang berpasangan dengan sekolah/program/siswa
    r'makan(?:an)?\s+bergizi.{0,35}(?:gratis|anak\s+sekolah|siswa|murid|santri|nasional|apbn|program\s+pemerintah|stunting)|'
    r'(?:program|proyek|kebijakan|janji|uji\s*coba|anggaran|subsidi)\s+(?:makan\s+siang|makan(?:an)?\s+bergizi|makan\s+gratis)|'
    r'makan\s+siang.{0,35}(?:gratis|sekolah|siswa|murid|anak\s+sd|anak\s+smp|presiden|pemerintah)|'
    # "makan gratis" untuk anak/sekolah/stunting/pemerintah
    r'(?:dikasih|bagi-bagi|program)\s+makan\s+gratis|'
    r'makan\s+gratis.{0,30}(?:anak|siswa|sekolah|stunting|rakyat|apbn)',
    re.I
)

# --- B. PATTERNS SEKOLAH RAKYAT ---
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

# Co-occurrence untuk Sekolah Rakyat: sekolah gratis / asrama / kemendikdasmen dalam konteks kebijakan publik
pat_sr_cooccur = re.compile(
    r'(?:sekolah|pendidikan)\s+gratis.{0,40}(?:rakyat|miskin|prabowo|pemerintah|program|asta\s*cita|asrama|daerah\s+terpencil|3t\b)|'
    r'(?:prabowo|gibran|pemerintah).{0,40}(?:sekolah\s+gratis|sekolah\s+rakyat|pendidikan\s+gratis)|'
    r'kemendikdasmen.{0,40}(?:sekolah|kurikulum|guru|rakyat|program)|'
    r'sekolah\s+berasrama.{0,40}(?:gratis|rakyat|pemerintah|prabowo)',
    re.I
)

# --- C. PATTERNS KDMP (Koperasi Desa Merah Putih) ---
pat_kdmp_core = re.compile(
    r'\bkdmp\b|'
    r'koperasi\s+desa\s+merah\s+putih|'
    r'koperasi\s+merah\s+putih|'
    r'desa\s+merah\s+putih',
    re.I
)

# Co-occurrence untuk KDMP: Koperasi / Dana Desa / BUMDes / Kopdes dalam konteks ekonomi desa / program
pat_kdmp_cooccur = re.compile(
    r'(?:koperasi\s+desa|kopdes|bumdes).{0,40}(?:merah\s+putih|prabowo|program|pangan|distribusi|petani|nelayan|mbg|dana\s+desa|modal|umkm)|'
    r'(?:program|proyek|kebijakan).{0,40}(?:koperasi\s+desa|desa\s+mandiri\s+pangan|kdmp|kopdes)|'
    r'koperasi\s+umkm\s+desa|'
    r'dana\s+desa.{0,40}(?:koperasi|bumdes|ketahanan\s+pangan)',
    re.I
)

# --- D. NEGATIVE NOISE EXCLUSIONS (Filter Sampah Lintas Topik) ---
pat_noise_filter = re.compile(
    # Curhat Bumil / Parenting / Laktasi murni
    r'pejuang\s+garis\s+dua|promil|senam\s+hamil|yoga\s+hamil|'
    r'booster\s+asi|laktasi|asi\s+eksklusif|sufor|pompa\s+asi|kantung\s+asi|kantong\s+asi|'
    r'usg\s+(?:2d|3d|4d)|bbj\s+janin|periksa\s+kandungan|'
    r'beli\s+2\s+gratis\s+1|promo\s+diskon|beli\s+susu\s+di\s+(?:indomaret|alfamart)|'
    # Isu Malaysia / Jerebu / Kabut Asap luar negeri
    r'kpm\s+dan\s+kkm|isu\s+jerebu|bakar\s+hutan\s+korang|menteri\s+malaysia|'
    # Isu Politik Nyasar tanpa sentuhan program
    r'ijazah\s+(?:jokowi|gibran)|fufufafa|maling\s+motor|kopassus|jis\s+dapat|ikn\s+mangkrak|'
    r'saham\s+bbca|laba\s+q1|'
    # Slang & topik lain
    r'naik\s+ompreng|mobil\s+ompreng|racun\s+shopee|racun\s+tiktok|'
    r'running\s+threads|lari\s+setiap\s+hari|yg\s+indigo|sk\s+pns\s+ku|freedive',
    re.I
)

# Evaluasi kelayakan
is_mbg_valid = content.str.contains(pat_mbg_core) | content.str.contains(pat_mbg_cooccur)
is_sr_valid = content.str.contains(pat_sr_core) | content.str.contains(pat_sr_cooccur)
is_kdmp_valid = content.str.contains(pat_kdmp_core) | content.str.contains(pat_kdmp_cooccur)

is_any_valid = is_mbg_valid | is_sr_valid | is_kdmp_valid
hits_noise = content.str.contains(pat_noise_filter)

# Keputusan Simpan / Buang:
# 1. Tidak boleh reply
# 2. Harus valid salah satu topik
# 3. Tidak boleh terkena filter noise (kecuali jika eksplisit menyebut anchor core seperti 'MBG', 'KDMP', 'Sekolah Rakyat')
has_strong_core = (
    content.str.contains(pat_mbg_core) | 
    content.str.contains(pat_sr_core) | 
    content.str.contains(pat_kdmp_core)
)

keep_mask = (~is_reply) & is_any_valid & (~hits_noise | has_strong_core)
discard_mask = ~keep_mask

print("\n" + "=" * 80)
print("HASIL SIMULASI KOMPREHENSIF (SELURUH TOPIK DARI BEFORE_FILTER)")
print("=" * 80)
print(f"Total Baris Diproses      : {len(df):,}")
print(f"✅ TOTAL LOLOS (DISIMPAN)  : {keep_mask.sum():,} ({keep_mask.sum()/len(df)*100:.1f}%)")
print(f"❌ TOTAL DIBUANG           : {discard_mask.sum():,} ({discard_mask.sum()/len(df)*100:.1f}%)")
print(f"   - Kategori Reply        : {is_reply.sum():,} baris")
print(f"   - Kategori Noise/Nyasar : {(discard_mask & ~is_reply).sum():,} baris")

print("\nRincian Data Lolos per Topik (Berdasarkan Topik Asli):")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    cnt = (keep_mask & (df['topic'] == t)).sum()
    total_t = (df['topic'] == t).sum()
    print(f"   - {t:16}: {cnt:,} / {total_t:,} baris ({cnt/total_t*100:.1f}%)")
