import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
content_str = df['content'].fillna('').astype(str)
is_reply = content_str.str.contains(r'Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@', case=False)
df_non_reply = df[~is_reply]

print("=== KDMP Non-reply Samples ===")
kdmp = df_non_reply[df_non_reply['topic'] == 'KDMP']
print(f"Total KDMP non-reply: {len(kdmp)}")
for _, row in kdmp.sample(min(10, len(kdmp)), random_state=42).iterrows():
    c = row['content'].replace('\n', ' ')
    print(f"- [{row['keyword']}] {c[:120]}")

print("\n=== Sekolah Rakyat Non-reply Samples ===")
sr = df_non_reply[df_non_reply['topic'] == 'Sekolah_Rakyat']
print(f"Total Sekolah_Rakyat non-reply: {len(sr)}")
for _, row in sr.sample(min(10, len(sr)), random_state=42).iterrows():
    c = row['content'].replace('\n', ' ')
    print(f"- [{row['keyword']}] {c[:120]}")
