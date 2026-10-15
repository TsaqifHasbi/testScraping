import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df_kand = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
print('Total rows in updated kandidat hapus:', len(df_kand))

# Check reasons
print(df_kand['alasan_rekomendasi_hapus'].value_counts())

non_reply_kand = df_kand[df_kand['alasan_rekomendasi_hapus'].str.contains('Algoritmik', case=False)]
print('\nTotal non-reply in kandidat:', len(non_reply_kand))

test_words = ['makan bergizi', 'makanan bergizi', 'makan gratis', 'makanan gratis', 'makan siang', 'mbg', 'koperasi', 'sekolah rakyat']
for w in test_words:
    cnt = non_reply_kand['content'].fillna('').str.contains(w, case=False).sum()
    print(f'Mentions "{w}": {cnt}')
