import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

files = {
    'Facebook': 'ScrapeData/scraped_Facebook_Only.csv',
    'Instagram': 'ScrapeData/scraped_Instagram_Only.csv',
    'TikTok': 'ScrapeData/scraped_TikTok_Only.csv',
    'Twitter': 'ScrapeData/scraped_Twitter_Only.csv',
    'YouTube': 'ScrapeData/scraped_YouTube_Only.csv'
}

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
        r'(?:sekolah\s+rakyat|sekolah\s+gratis\s+rakyat|pendidikan\s+sekolah\s+rakyat|kemendikdasmen\s+sekolah\s+rakyat|sekolah\s+gratis)',
        re.IGNORECASE
    )
}

print("=== CHECKING NON-MATCHING SAMPLES IN OTHER PLATFORMS ===")
for name, path in files.items():
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path, low_memory=False)
    print(f"\n=================== {name} ===================")
    for t in ['Sekolah_Rakyat', 'KDMP', 'MBG']:
        sub = df[df['topic'] == t]
        if len(sub) == 0:
            continue
        pat = PATTERNS[t]
        not_matched = sub[~sub['content'].astype(str).str.contains(pat)]
        print(f"Topik {t}: {len(not_matched)} / {len(sub)} ({len(not_matched)/len(sub)*100:.1f}%) non-matched")
        if len(not_matched) > 0:
            print("  Contoh 2 postingan non-matched:")
            for idx, r in not_matched.head(2).iterrows():
                print(f"    [kw: {r['keyword']}] {repr(str(r['content'])[:90])}")
