import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only.csv', low_memory=False)
mbg = df[df['topic'] == 'MBG']

# Strictly unambiguous MBG anchors:
strict_mbg = re.compile(
    r'\bmbg\b|'
    r'makan(?:an)?\s+bergizi\s+gratis|'
    r'makan(?:an)?\s+gratis\s+bergizi|'
    r'makan\s+siang\s+gratis|'
    r'badan\s+gizi\s+nasional|\bbgn\b|'
    r'dadan\s+hindayana|\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
    r'dapur\s+(?:gizi|mbg|sehat|komunal)|'
    r'(?:prabowo|gibran).{0,30}(?:makan|gizi|susu|program)',
    re.IGNORECASE
)

# Non-strict matches (only matched loose patterns)
loose = mbg[~mbg['content'].fillna('').str.contains(strict_mbg)]
print(f"Total MBG rows in filtered CSV: {len(mbg):,}")
print(f"Rows with STRICT MBG anchor: {len(mbg) - len(loose):,}")
print(f"Rows with ONLY LOOSE/SARCASM patterns (potential false positives): {len(loose):,}")

print("\n--- Inspecting why loose rows matched ---")
loose_checks = {
    'makan siang': r'makan(?:an)?.{0,25}siang',
    'makanan gratis': r'makan(?:an)?.{0,25}gratis',
    'makanan bergizi': r'makan(?:an)?.{0,25}bergizi',
    'keracunan': r'keracunan|beracun',
    'ompreng': r'ompreng',
    'susu': r'susu\s+(?:basi|ikan|gratis|uht)',
    'menu 10rb/15rb': r'menu\s+(?:10\s*rb|15\s*rb)',
    'janji makan': r'janji\s+(?:manis\s+)?makan',
    'anggaran makan/gizi': r'anggaran\s+(?:mbg|makan|gizi)',
    'uji coba makan': r'uji\s+coba\s+makan',
    'vendor/katering': r'vendor\s+makan|katering\s+makan',
}

for name, pat in loose_checks.items():
    cnt = loose['content'].fillna('').str.contains(pat, case=False).sum()
    print(f"  - Matched '{name}': {cnt:,}")

print("\n" + "="*80)
print("SAMPLES OF LOOSE ROWS TO CHECK RELEVANCY:")
print("="*80)
for idx, r in loose.sample(n=min(30, len(loose)), random_state=42).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:150]}")
    print("-" * 50)
