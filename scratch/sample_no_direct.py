import sys
import io
import pandas as pd
import re
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)
mbg = df[df['topic'] == 'MBG'].copy()
content = mbg['content'].fillna('').astype(str)

is_reply = content.str.contains(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.I)

direct_gov_mbg = re.compile(
    r'\bmbg\b|'
    r'makan(?:an)?\s+bergizi\s+gratis|'
    r'makan(?:an)?\s+gratis\s+bergizi|'
    r'makan\s+siang\s+gratis|'
    r'badan\s+gizi\s+nasional|\bbgn\b|'
    r'dadan\s+hindayana|\bsppg\b|'
    r'satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
    r'dapur\s+(?:gizi|mbg|sehat|komunal)|'
    r'(?:program|kebijakan|proyek|uji\s*coba|anggaran|realisasi|janji)\s+(?:makan|gizi|mbg)|'
    r'(?:prabowo|gibran).{0,30}(?:makan|gizi|susu|program)',
    re.I
)

has_direct = content.str.contains(direct_gov_mbg)
no_direct = mbg[~has_direct & ~is_reply]

print("Sampling 25 rows from no_direct across different keywords:")
for kw in ['makan bergizi gratis ibu hamil', 'MBG berhasil', 'korupsi MBG', 'makanan bergizi gratis siswa', 'MBG kritik']:
    sub = no_direct[no_direct['keyword'] == kw]
    print(f"\n=== KEYWORD: {kw} (Total {len(sub):,} rows) ===")
    for idx, r in sub.head(5).iterrows():
        c = str(r['content']).replace('\n', ' ')
        print(f"[{r['handle']}] {c[:140]}")
