import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

path = 'ScrapeData/scraped_Threads_Only.csv'
df = pd.read_csv(path, low_memory=False)

print(f"Total Rows in Threads: {len(df)}")

# Check replies
is_reply = df['content'].dropna().astype(str).str.contains(r'^(?:Membalas\s+@|Replying\s+to\s+@)', case=False, regex=True)
print(f"Total replies ('Membalas @...' or 'Replying to @...'): {is_reply.sum()} ({is_reply.sum()/len(df)*100:.1f}%)")

# Also check any @ mentions at start
is_mention_start = df['content'].dropna().astype(str).str.contains(r'^@\w+', regex=True)
print(f"Total starting with @handle: {is_mention_start.sum()}")

# Check sample replies
print("\n--- Contoh Konten Balasan / Reply (5 sampel) ---")
for idx, c in df[is_reply]['content'].head(5).items():
    print(f"[{idx}] {repr(c[:120])}")

# Let's inspect rows by topic that do NOT match the core pattern
PATTERNS = {
    'MBG': re.compile(
        r'(?:\bmbg\b|makan\s+bergizi\s+gratis|makan\s+siang\s+gratis|badan\s+gizi\s+nasional|\bbgn\b|\bsppg\b|satuan\s+pelayanan\s+pemenuhan\s+gizi|dapur\s+(?:gizi|mbg|sehat)|menu\s+mbg|anggaran\s+mbg|keracunan\s+mbg|kasus\s+mbg|uji\s+coba\s+mbg)',
        re.IGNORECASE
    ),
    'KDMP': re.compile(
        r'(?:\bkdmp\b|koperasi\s+desa|desa\s+merah\s+putih|koperasi\s+merah\s+putih|desa\s+mandiri\s+pangan|\bkoperasi\b|dana\s+desa\s+koperasi|koperasi\s+umkm\s+desa|bumdes)',
        re.IGNORECASE
    ),
    'Sekolah_Rakyat': re.compile(
        r'(?:sekolah\s+rakyat|sekolah\s+gratis\s+rakyat|pendidikan\s+sekolah\s+rakyat|kemendikdasmen\s+sekolah\s+rakyat)',
        re.IGNORECASE
    )
}

print("\n--- Sampel Konten Tidak Relevan per Topik ---")
for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
    sub = df[df['topic'] == t]
    pat = PATTERNS[t]
    not_rel = sub[~sub['content'].astype(str).str.contains(pat)]
    print(f"\nTopik {t}: {len(not_rel)} tidak relevan dari {len(sub)} total baris")
    print("Contoh 5 postingan yang tidak relevan:")
    for idx, r in not_rel.head(5).iterrows():
        print(f"  [kw: {r['keyword']}] Content: {repr(str(r['content'])[:100])}")
