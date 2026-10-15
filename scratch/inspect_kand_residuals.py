import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df_kand = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
non_reply_kand = df_kand[df_kand['alasan_rekomendasi_hapus'].str.contains('Algoritmik', case=False)]

mbg_in_kand = non_reply_kand[non_reply_kand['content'].fillna('').str.contains(r'\bmbg\b', case=False, regex=True)]
print(f"Total with word boundary \\bmbg\\b: {len(mbg_in_kand)}")

print("\nSample rows with \\bmbg\\b in non_reply_kand:")
for idx, r in mbg_in_kand.head(10).iterrows():
    c = r['content'].replace('\n', ' ')
    print(f"- [Topic: {r['topic']}, Keyword: {r['keyword']}] {c[:120]}")

makan_in_kand = non_reply_kand[non_reply_kand['content'].fillna('').str.contains(r'makan(?:an)?\s+bergizi', case=False, regex=True)]
print(f"\nTotal with makan(an) bergizi in non_reply_kand: {len(makan_in_kand)}")
for idx, r in makan_in_kand.head(10).iterrows():
    c = r['content'].replace('\n', ' ')
    print(f"- [Topic: {r['topic']}, Keyword: {r['keyword']}] {c[:120]}")
