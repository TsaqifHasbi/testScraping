import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

df_raw = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)
is_meta = (
    df_raw['handle'].fillna('').astype(str).str.lower().str.strip().isin(['@meta.ai', 'meta.ai'])
) | (
    df_raw['url'].fillna('').astype(str).str.contains(r'threads\.net/@meta\.ai', case=False, na=False)
)
df = df_raw[~is_meta].copy().reset_index(drop=True)
content = df['content'].fillna('').astype(str)

reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
    re.I
)
is_reply = content.str.contains(reply_pat)

# Re-run pattern definitions
pat_sr_core = re.compile(r'sekolah\s+rakyat|sekolah\s+gratis\s+rakyat|sekolah\s+rakyat\s+gratis|pendidikan\s+sekolah\s+rakyat|sekolah\s+negeri\s+rakyat|sekolah\s+rakyat\s+berasrama|program\s+sekolah\s+rakyat', re.I)
pat_sr_cooccur = re.compile(r'(?:sekolah|pendidikan)\s+gratis.{0,40}(?:rakyat|miskin|prabowo|pemerintah|program|asta\s*cita|asrama|daerah\s+terpencil|3t\b)|(?:prabowo|gibran|pemerintah).{0,40}(?:sekolah\s+gratis|sekolah\s+rakyat|pendidikan\s+gratis)|kemendikdasmen.{0,40}(?:sekolah|kurikulum|guru|rakyat|program)|sekolah\s+berasrama.{0,40}(?:gratis|rakyat|pemerintah|prabowo)', re.I)

pat_kdmp_core = re.compile(r'\bkdmp\b|koperasi\s+desa\s+merah\s+putih|koperasi\s+merah\s+putih|desa\s+merah\s+putih', re.I)
pat_kdmp_cooccur = re.compile(r'(?:koperasi\s+desa|kopdes|bumdes).{0,40}(?:merah\s+putih|prabowo|program|pangan|distribusi|petani|nelayan|mbg|dana\s+desa|modal|umkm)|(?:program|proyek|kebijakan).{0,40}(?:koperasi\s+desa|desa\s+mandiri\s+pangan|kdmp|kopdes)|koperasi\s+umkm\s+desa|dana\s+desa.{0,40}(?:koperasi|bumdes|ketahanan\s+pangan)', re.I)

pat_mbg_core = re.compile(r'\bmbg\b|makan(?:an)?\s+bergizi\s+gratis|makan(?:an)?\s+gratis\s+bergizi|makan\s+siang\s+gratis|makan\s+gratis\s+siang|makan\s+bergizi\s+gak\s+gratis|makan\s+bergizi\s+tentunya\s+tidak\s+gratis|badan\s+gizi\s+nasional|\bbgn\b|dadan\s+hindayana|\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|dapur\s+(?:gizi|mbg|sehat|komunal)|murderer\s+by\s+government|badan\s+genosida\s+negara|(?:prabowo|gibran).{0,35}(?:makan|gizi|susu|ompreng|bgn)', re.I)
pat_mbg_cooccur = re.compile(r'(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun).{0,60}(?:siswa|murid|anak|sekolah|sd\b|smp\b|sma\b|santri|pesantren|program|gratis|uji\s*coba|massal|katering|dapur|vendor|ompreng|korban)|(?:siswa|murid|anak|sekolah|santri|pesantren|warga|korban).{0,60}(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun)|ompreng.{0,50}(?:makan|lauk|nasi|sayur|cuci|dapur|sekolah|anak|siswa|murid|guru|katering|program|sticker|stiker|relawan)|(?:makan|cuci|wadah|tempat|piring|katering|dapur|guru|siswa|relawan).{0,50}ompreng|susu\s+ikan|susu.{0,40}(?:mbg|bgn|gratis|program|sekolah|siswa|anak|murid|pengganti\s+susu|impor|peternak|sapi|lokal)|(?:menu|porsi|anggaran|biaya|alokasi).{0,40}(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu|71\s*t|triliun|335\s*t|apbn|per\s+porsi|per\s+anak)|(?:program|uji\s*coba|katering|vendor).{0,40}(?:10\s*rb|15\s*rb|porsi|nasi)|makan(?:an)?\s+bergizi.{0,35}(?:gratis|anak\s+sekolah|siswa|murid|santri|nasional|apbn|program\s+pemerintah|stunting)|(?:program|proyek|kebijakan|janji|uji\s*coba|anggaran|subsidi)\s+(?:makan\s+siang|makan(?:an)?\s+bergizi|makan\s+gratis)|makan\s+siang.{0,35}(?:gratis|sekolah|siswa|murid|anak\s+sd|anak\s+smp|presiden|pemerintah)|(?:dikasih|bagi-bagi|program)\s+makan\s+gratis|makan\s+gratis.{0,30}(?:anak|siswa|sekolah|stunting|rakyat|apbn)', re.I)

pat_noise_filter = re.compile(
    r'pejuang\s+garis\s+dua|promil|senam\s+hamil|yoga\s+hamil|'
    r'booster\s+asi|laktasi|asi\s+eksklusif|sufor|pompa\s+asi|kantung\s+asi|kantong\s+asi|'
    r'usg\s+(?:2d|3d|4d)|bbj\s+janin|periksa\s+kandungan|'
    r'beli\s+2\s+gratis\s+1|promo\s+diskon|beli\s+susu\s+di\s+(?:indomaret|alfamart)|'
    r'kpm\s+dan\s+kkm|isu\s+jerebu|bakar\s+hutan\s+korang|menteri\s+malaysia|'
    r'ijazah\s+(?:jokowi|gibran)|fufufafa|maling\s+motor|kopassus|jis\s+dapat|ikn\s+mangkrak|'
    r'saham\s+bbca|laba\s+q1|'
    r'naik\s+ompreng|mobil\s+ompreng|racun\s+shopee|racun\s+tiktok|'
    r'running\s+threads|lari\s+setiap\s+hari|yg\s+indigo|sk\s+pns\s+ku|freedive',
    re.I
)

is_mbg_valid = content.str.contains(pat_mbg_core) | content.str.contains(pat_mbg_cooccur)
is_sr_valid = content.str.contains(pat_sr_core) | content.str.contains(pat_sr_cooccur)
is_kdmp_valid = content.str.contains(pat_kdmp_core) | content.str.contains(pat_kdmp_cooccur)
is_any_valid = is_mbg_valid | is_sr_valid | is_kdmp_valid
hits_noise = content.str.contains(pat_noise_filter)

has_strong_core = (
    content.str.contains(pat_mbg_core) | 
    content.str.contains(pat_sr_core) | 
    content.str.contains(pat_kdmp_core)
)

keep_mask = (~is_reply) & is_any_valid & (~hits_noise | has_strong_core)
discard_mask = ~keep_mask

# Check sample discarded from KDMP non-reply
disc_kdmp = df[discard_mask & ~is_reply & (df['topic'] == 'KDMP')]
print("=" * 80)
print(f"SAMPLE DISCARDED NON-REPLY DARI KDMP (Total: {len(disc_kdmp):,}):")
print("=" * 80)
for idx, r in disc_kdmp.sample(n=10, random_state=42).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}")

disc_sr = df[discard_mask & ~is_reply & (df['topic'] == 'Sekolah_Rakyat')]
print("\n" + "=" * 80)
print(f"SAMPLE DISCARDED NON-REPLY DARI SEKOLAH_RAKYAT (Total: {len(disc_sr):,}):")
print("=" * 80)
for idx, r in disc_sr.sample(n=10, random_state=42).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}")
