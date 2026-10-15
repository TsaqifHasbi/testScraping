import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)
mbg = df[df['topic'] == 'MBG'].copy()
content = mbg['content'].fillna('').astype(str)

is_reply = content.str.contains(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.I)

pat_core_anchor = re.compile(
    r'\bmbg\b|'
    r'makan(?:an)?\s+bergizi\s+gratis|'
    r'makan(?:an)?\s+gratis\s+bergizi|'
    r'makan\s+siang\s+gratis|'
    r'makan\s+gratis\s+siang|'
    r'badan\s+gizi\s+nasional|\bbgn\b|'
    r'dadan\s+hindayana|\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
    r'dapur\s+(?:gizi|mbg|sehat|komunal)|'
    r'murderer\s+by\s+government|badan\s+genosida\s+negara|'
    r'(?:prabowo|gibran).{0,35}(?:makan|gizi|susu|ompreng|bgn)',
    re.I
)

pat_poison_context = re.compile(
    r'(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun).{0,60}(?:siswa|murid|anak|sekolah|sd\b|smp\b|sma\b|santri|pesantren|program|gratis|uji\s*coba|massal|katering|dapur|vendor|ompreng|korban)|'
    r'(?:siswa|murid|anak|sekolah|santri|pesantren|warga|korban).{0,60}(?:keracunan|beracun|makan(?:an)?\s+basi|makan\s+beracun)',
    re.I
)
pat_poison_noise = re.compile(r'racun\s+(?:shopee|tiktok)|keracunan\s+(?:cinta|drakor|seafood|jamur|alkohol|oplosan|karbon|asap)|kucing.{0,30}keracunan', re.I)

pat_ompreng_context = re.compile(
    r'ompreng.{0,50}(?:makan|lauk|nasi|sayur|cuci|dapur|sekolah|anak|siswa|murid|guru|katering|program|sticker|stiker|relawan)|'
    r'(?:makan|cuci|wadah|tempat|piring|katering|dapur|guru|siswa|relawan).{0,50}ompreng',
    re.I
)
pat_ompreng_car = re.compile(r'naik\s+ompreng|mobil\s+ompreng|omprengan\s+jalan\s+kaki|tumpangan', re.I)

pat_susu_context = re.compile(
    r'susu\s+ikan|'
    r'susu.{0,40}(?:mbg|bgn|gratis|program|sekolah|siswa|anak|murid|pengganti\s+susu|impor|peternak|sapi|lokal)',
    re.I
)

pat_menu_budget_context = re.compile(
    r'(?:menu|porsi|anggaran|biaya|alokasi).{0,40}(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu|71\s*t|triliun|335\s*t|apbn|per\s+porsi|per\s+anak)|'
    r'(?:program|uji\s*coba|katering|vendor).{0,40}(?:10\s*rb|15\s*rb|porsi|nasi)',
    re.I
)

pat_generic_food_context = re.compile(
    r'makan(?:an)?\s+bergizi.{0,35}(?:gratis|anak\s+sekolah|siswa|murid|santri|nasional|apbn|program\s+pemerintah)|'
    r'(?:program|proyek|kebijakan|janji|uji\s*coba|anggaran|subsidi)\s+(?:makan\s+siang|makan(?:an)?\s+bergizi|makan\s+gratis)|'
    r'makan\s+siang.{0,35}(?:gratis|sekolah|siswa|murid|anak\s+sd|anak\s+smp|presiden|pemerintah)',
    re.I
)

pat_pure_noise = re.compile(
    r'pejuang\s+garis\s+dua|promil|senam\s+hamil|yoga\s+hamil|'
    r'booster\s+asi|laktasi|asi\s+eksklusif|sufor|pompa\s+asi|kantung\s+asi|kantong\s+asi|'
    r'usg\s+(?:2d|3d|4d)|bbj\s+janin|periksa\s+kandungan|bidan\s+desa|'
    r'beli\s+2\s+gratis\s+1|promo\s+diskon|beli\s+susu\s+di\s+(?:indomaret|alfamart)|'
    r'ijazah\s+(?:jokowi|gibran)|fufufafa|maling\s+motor|kopassus|jis\s+dapat|ikn\s+mangkrak|'
    r'lempeng\s+aktif|gempa|karhutla|banjir\s+bandang|'
    r'naik\s+ompreng|mobil\s+ompreng|racun\s+shopee|racun\s+tiktok',
    re.I
)

is_core = content.str.contains(pat_core_anchor)
is_poison_valid = content.str.contains(pat_poison_context) & ~content.str.contains(pat_poison_noise)
is_ompreng_valid = content.str.contains(pat_ompreng_context) & ~content.str.contains(pat_ompreng_car)
is_susu_valid = content.str.contains(pat_susu_context)
is_menu_valid = content.str.contains(pat_menu_budget_context)
is_food_valid = content.str.contains(pat_generic_food_context)

has_contextual = is_poison_valid | is_ompreng_valid | is_susu_valid | is_menu_valid | is_food_valid
is_relevant = (is_core | has_contextual) & ~is_reply
hits_pure_noise = content.str.contains(pat_pure_noise)

final_keep = is_relevant & (~hits_pure_noise | is_core)
final_discard = ~final_keep

discarded_non_reply = mbg[final_discard & ~is_reply]

print("="*80)
print("SAMPLE DISCARDED NON-REPLY POSTS (Noise identified):")
print("="*80)
for idx, r in discarded_non_reply.sample(n=min(25, len(discarded_non_reply)), random_state=42).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}")
    print("-" * 40)
