import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

files = {
    'Facebook': 'ScrapeData/scraped_Facebook_Only.csv',
    'Instagram': 'ScrapeData/scraped_Instagram_Only.csv',
    'News': 'ScrapeData/scraped_News_Only.csv',
    'Threads': 'ScrapeData/scraped_Threads_Only.csv',
    'TikTok': 'ScrapeData/scraped_TikTok_Only.csv',
    'Twitter': 'ScrapeData/scraped_Twitter_Only.csv',
    'YouTube': 'ScrapeData/scraped_YouTube_Only.csv'
}

# Regex patterns for core topic relevance
# MBG:
# "mbg", "makan bergizi gratis", "makan siang gratis", "badan gizi", "bgn", "sppg", "satuan pelayanan pemenuhan gizi", "dapur gizi"
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

print("=== EVALUASI KORELASI KONTEN DENGAN TOPIK DI SELURUH PLATFORM ===")
for name, path in files.items():
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path, low_memory=False)
    content_col = 'content' if 'content' in df.columns else None
    topic_col = 'topic' if 'topic' in df.columns else None
    
    if not content_col:
        print(f"[{name}] Kolom content tidak ditemukan!")
        continue
        
    print(f"\n--- Platform: {name} (Total Data: {len(df)}) ---")
    
    # If topic column exists, analyze per topic
    if topic_col:
        for t in ['MBG', 'KDMP', 'Sekolah_Rakyat']:
            sub = df[df[topic_col] == t]
            if len(sub) == 0:
                continue
            pat = PATTERNS.get(t)
            match_count = sub[content_col].dropna().astype(str).str.contains(pat).sum()
            pct = (match_count / len(sub)) * 100 if len(sub) > 0 else 0
            print(f"  Topik {t:<15}: {match_count:>6} / {len(sub):>6} baris relevan ({pct:>5.1f}%)")
    else:
        # Check overall
        all_pat = re.compile(r'|'.join([p.pattern for p in PATTERNS.values()]), re.IGNORECASE)
        match_count = df[content_col].dropna().astype(str).str.contains(all_pat).sum()
        pct = (match_count / len(df)) * 100
        print(f"  Total Relevan ke salah satu topik: {match_count} / {len(df)} ({pct:.1f}%)")
