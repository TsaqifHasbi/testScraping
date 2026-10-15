import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

threads_path = 'ScrapeData/scraped_Threads_Only.csv'
df = pd.read_csv(threads_path, low_memory=False)

print(f"Loaded Threads dataset: {len(df)} rows")

# Regex patterns for core topic relevance
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

reply_pat = re.compile(r'^(?:Membalas\s+@|Replying\s+to\s+@)', re.IGNORECASE)

content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(reply_pat)

has_topic_kw = pd.Series(False, index=df.index)
for t, pat in PATTERNS.items():
    mask = (df['topic'] == t)
    has_topic_kw[mask] = content_str[mask].str.contains(pat)

# 1. Main posts that are relevant
cat_a = (~is_reply) & (has_topic_kw) # 145,147
# 2. Replies that explicitly mention topic
cat_b = (is_reply) & (has_topic_kw)  # 6,802
# 3. Replies that do NOT mention topic (lost context)
cat_c = (is_reply) & (~has_topic_kw) # 15,923
# 4. Algorithmic recommendations / completely unrelated
cat_d = (~is_reply) & (~has_topic_kw) # 57,505

print(f"Cat A (Main Post Relevan)    : {cat_a.sum():>6}")
print(f"Cat B (Reply Sebut Topik)    : {cat_b.sum():>6}")
print(f"Cat C (Reply Tanpa Konteks)  : {cat_c.sum():>6}")
print(f"Cat D (Algoritmik Nyasar)    : {cat_d.sum():>6}")

# Create reason for irrelevant rows
irrelevant_mask = cat_c | cat_d
df_irrelevant = df[irrelevant_mask].copy()
reasons = []
for idx in df_irrelevant.index:
    if cat_c[idx]:
        reasons.append('Reply / Diskusi Kehilangan Konteks (Membalas @... tanpa kata kunci)')
    else:
        reasons.append('Rekomendasi Algoritmik / Konten Nyasar (Tanpa kata kunci tema besar)')
df_irrelevant['alasan_rekomendasi_hapus'] = reasons

# Save quarantine/candidate file
quarantine_path = 'ScrapeData/scraped_Threads_Kandidat_Hapus.csv'
df_irrelevant.to_csv(quarantine_path, index=False, encoding='utf-8')
print(f"Saved candidate deletion file to {quarantine_path} ({len(df_irrelevant)} rows)")

# Save cleaned version (Cat A + Cat B, or Cat A only)
df_clean_all_relevant = df[has_topic_kw].copy()
clean_path = 'ScrapeData/scraped_Threads_Only_RELEVAN.csv'
df_clean_all_relevant.to_csv(clean_path, index=False, encoding='utf-8')
print(f"Saved clean relevant dataset to {clean_path} ({len(df_clean_all_relevant)} rows)")
