import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)
mbg = df[df['topic'] == 'MBG'].copy()
content = mbg['content'].fillna('').astype(str)

print(f"Total MBG rows in BEFORE_FILTER: {len(mbg):,}")

# 1. Reply / Mention patterns
is_reply = content.str.contains(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.I)
print(f"Reply / Balasan: {is_reply.sum():,} ({is_reply.sum()/len(mbg)*100:.1f}%)")

# 2. Check explicitly mentions MBG/Program/Gov anchors
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
print(f"Has Direct Gov/MBG Anchor: {has_direct.sum():,} ({has_direct.sum()/len(mbg)*100:.1f}%)")

# 3. Look at rows WITHOUT direct anchor
no_direct = mbg[~has_direct & ~is_reply]
print(f"Non-reply without direct anchor: {len(no_direct):,}")

# What keywords did these non-direct rows come from?
print("\nTop keywords for non-reply rows without direct anchor:")
print(no_direct['keyword'].value_counts().head(15))
