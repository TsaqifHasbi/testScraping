import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

df = pd.read_csv('ScrapeData/scraped_Threads_Only.csv', low_memory=False)
print(f"Total Rows: {len(df)}")

# Reply pattern
reply_pat = re.compile(r'^(?:Membalas\s+@|Replying\s+to\s+@)', re.IGNORECASE)

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

content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(reply_pat)

has_topic_kw = pd.Series(False, index=df.index)
for t, pat in PATTERNS.items():
    mask = (df['topic'] == t)
    has_topic_kw[mask] = content_str[mask].str.contains(pat)

print(f"\nBreakdown Threads (Total: {len(df)}):")
cat_a = (~is_reply) & (has_topic_kw) # Main post relevant
cat_b = (is_reply) & (has_topic_kw)  # Reply relevant (mentions topic)
cat_c = (is_reply) & (~has_topic_kw) # Reply irrelevant (no topic mentioned)
cat_d = (~is_reply) & (~has_topic_kw) # Main post irrelevant (algorithmic noise / no topic)

print(f"1. Main Post RELEVAN (Ada kata kunci tema besar): {cat_a.sum():>6} ({cat_a.sum()/len(df)*100:>5.1f}%) -> SIMPAN (Sangat Bersih)")
print(f"2. Reply RELEVAN (Membalas @..., tapi menyebut tema besar): {cat_b.sum():>6} ({cat_b.sum()/len(df)*100:>5.1f}%) -> Opsional")
print(f"3. Reply TIDAK RELEVAN (Membalas @..., tanpa kata kunci): {cat_c.sum():>6} ({cat_c.sum()/len(df)*100:>5.1f}%) -> HAPUS")
print(f"4. Main Post TIDAK RELEVAN (Rekomendasi Algoritmik/Nyasar): {cat_d.sum():>6} ({cat_d.sum()/len(df)*100:>5.1f}%) -> HAPUS")

print("\n--- Contoh Cat 2: Reply tapi MENYEBUT tema besar (3 sampel) ---")
for idx, r in df[cat_b].head(3).iterrows():
    print(f"  [{r['topic']} - {r['keyword']}] {repr(r['content'][:120])}")

print("\n--- Contoh Cat 3: Reply TANPA tema besar (3 sampel) ---")
for idx, r in df[cat_c].head(3).iterrows():
    print(f"  [{r['topic']} - {r['keyword']}] {repr(r['content'][:120])}")

print("\n--- Contoh Cat 4: Main Post Algoritmik Nyasar (3 sampel) ---")
for idx, r in df[cat_d].head(3).iterrows():
    print(f"  [{r['topic']} - {r['keyword']}] {repr(r['content'][:120])}")
