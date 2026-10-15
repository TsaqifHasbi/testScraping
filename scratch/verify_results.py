import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df_main = pd.read_csv('ScrapeData/scraped_Threads_Only.csv', low_memory=False)
df_discard = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)

print('Main dataset count:', len(df_main))
print('Main dataset columns:', df_main.columns.tolist())
print('Candidate/Discarded dataset count:', len(df_discard))
print('Candidate columns:', df_discard.columns.tolist())

reply_pat = re.compile(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.IGNORECASE)
reply_in_main = df_main['content'].fillna('').astype(str).str.contains(reply_pat).sum()
print('Replies found in Main dataset:', reply_in_main)

sarcasm_words = ['beracun', 'makan beracun gratis', 'makanan beracun', 'keracunan', 'makanan basi', 'ompreng']
for w in sarcasm_words:
    c = df_main['content'].fillna('').astype(str).str.contains(w, case=False).sum()
    print(f'Count of "{w}" in main dataset: {c}')
