import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
content_str = df['content'].fillna('').astype(str)

# Exclude replies cleanly
is_reply = content_str.str.contains(r'Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@', case=False)
df_non_reply = df[~is_reply]

mbg_non_reply = df_non_reply[df_non_reply['topic'] == 'MBG']
print('Total MBG non-reply without loose reply:', len(mbg_non_reply))

sarcasm_terms = [
    'beracun', 'racun', 'keracunan', 'basi', 'ompreng', 'susu ikan',
    'makan beracun', 'makan basi', 'makanan basi', 'makanan beracun',
    'bukan bergizi', 'bagi racun', 'bagi-bagi racun'
]

for term in sarcasm_terms:
    m = mbg_non_reply['content'].str.contains(term, case=False, regex=False)
    print(f'{term:25}: {m.sum()}')

print('\n=== SAMPLES WITH BERACUN / RACUN ===')
beracun_sample = mbg_non_reply[mbg_non_reply['content'].str.contains(r'beracun|racun|keracunan', case=False)]
for _, row in beracun_sample.head(20).iterrows():
    c = row['content'].replace('\n', ' ')
    print(f"- [{row['keyword']}] {c[:140]}")
