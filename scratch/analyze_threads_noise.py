import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)
mbg = df[df['topic'] == 'MBG']

core_mbg = re.compile(r'\bmbg\b|makan(?:an)?\s+bergizi\s+gratis|makan\s+siang\s+gratis|badan\s+gizi\s+nasional|\bbgn\b|\bsppg\b|prabowo|gibran', re.I)

print("=" * 70)
print("1. SAMPLE KONTEN: 'makan siang' TANPA ANCHOR MBG")
print("=" * 70)
cond_ms = mbg['content'].fillna('').str.contains(r'makan\s+siang', case=False) & ~mbg['content'].fillna('').str.contains(core_mbg)
for idx, r in mbg[cond_ms].head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")

print("\n" + "=" * 70)
print("2. SAMPLE KONTEN: 'keracunan / beracun' TANPA ANCHOR MBG")
print("=" * 70)
cond_poison = mbg['content'].fillna('').str.contains(r'keracunan|beracun', case=False) & ~mbg['content'].fillna('').str.contains(core_mbg)
for idx, r in mbg[cond_poison].head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")

print("\n" + "=" * 70)
print("3. SAMPLE KONTEN: 'ompreng / omprengan' TANPA ANCHOR MBG")
print("=" * 70)
cond_omp = mbg['content'].fillna('').str.contains(r'ompreng', case=False) & ~mbg['content'].fillna('').str.contains(core_mbg)
for idx, r in mbg[cond_omp].head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")

print("\n" + "=" * 70)
print("4. SAMPLE KONTEN: 'makanan bergizi' TANPA KATA 'gratis' ATAU ANCHOR MBG")
print("=" * 70)
cond_gizi = mbg['content'].fillna('').str.contains(r'makan(?:an)?\s+bergizi', case=False) & ~mbg['content'].fillna('').str.contains(r'gratis', case=False) & ~mbg['content'].fillna('').str.contains(core_mbg)
for idx, r in mbg[cond_gizi].head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")
