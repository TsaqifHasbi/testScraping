import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)

print("=" * 80)
print("ANALYSIS OF SEKOLAH_RAKYAT")
print("=" * 80)
sr = df[df['topic'] == 'Sekolah_Rakyat'].copy()
sr_content = sr['content'].fillna('').astype(str)

sr_reply = sr_content.str.contains(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.I)
print(f"Total Sekolah_Rakyat: {len(sr):,}")
print(f"Reply / Balasan: {sr_reply.sum():,} ({sr_reply.sum()/len(sr)*100:.1f}%)")
print(f"Non-Reply Posts: {(~sr_reply).sum():,}")

# Check content matching for Sekolah Rakyat
sr_non_reply = sr[~sr_reply]
sr_has_sr = sr_non_reply['content'].fillna('').str.contains(r'sekolah\s+rakyat', re.I)
sr_has_sekolah_gratis = sr_non_reply['content'].fillna('').str.contains(r'sekolah\s+gratis|pendidikan\s+gratis', re.I)
sr_has_mbg = sr_non_reply['content'].fillna('').str.contains(r'\bmbg\b|makan\s+(?:bergizi|siang|gratis)', re.I)

print(f"Mentions 'sekolah rakyat': {sr_has_sr.sum():,} ({sr_has_sr.sum()/len(sr_non_reply)*100:.1f}%)")
print(f"Mentions 'sekolah gratis / pendidikan gratis': {sr_has_sekolah_gratis.sum():,} ({sr_has_sekolah_gratis.sum()/len(sr_non_reply)*100:.1f}%)")
print(f"Mentions 'MBG / makan siang / bergizi': {sr_has_mbg.sum():,} ({sr_has_mbg.sum()/len(sr_non_reply)*100:.1f}%)")

# What about rows with NONE of these?
sr_no_match = sr_non_reply[~sr_has_sr & ~sr_has_sekolah_gratis & ~sr_has_mbg]
print(f"Rows without any of those anchors (Potential Noise): {len(sr_no_match):,}")

print("\nSamples of SR potential noise:")
for idx, r in sr_no_match.head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")

print("\n" + "=" * 80)
print("ANALYSIS OF KDMP")
print("=" * 80)
kdmp = df[df['topic'] == 'KDMP'].copy()
kdmp_content = kdmp['content'].fillna('').astype(str)

kdmp_reply = kdmp_content.str.contains(r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)', re.I)
print(f"Total KDMP: {len(kdmp):,}")
print(f"Reply / Balasan: {kdmp_reply.sum():,} ({kdmp_reply.sum()/len(kdmp)*100:.1f}%)")
print(f"Non-Reply Posts: {(~kdmp_reply).sum():,}")

kdmp_non_reply = kdmp[~kdmp_reply]
kdmp_has_kdmp = kdmp_non_reply['content'].fillna('').str.contains(r'\bkdmp\b', re.I)
kdmp_has_kopdes = kdmp_non_reply['content'].fillna('').str.contains(r'koperasi\s+(?:desa|merah\s+putih|unit\s+desa|umkm|simpan\s+pinjam)|\bkoperasi\b', re.I)
kdmp_has_desa_mp = kdmp_non_reply['content'].fillna('').str.contains(r'desa\s+merah\s+putih|desa\s+mandiri', re.I)
kdmp_has_mbg = kdmp_non_reply['content'].fillna('').str.contains(r'\bmbg\b|makan\s+(?:bergizi|siang|gratis)', re.I)

print(f"Mentions 'KDMP': {kdmp_has_kdmp.sum():,}")
print(f"Mentions 'koperasi': {kdmp_has_kopdes.sum():,}")
print(f"Mentions 'desa merah putih': {kdmp_has_desa_mp.sum():,}")
print(f"Mentions 'MBG': {kdmp_has_mbg.sum():,}")

kdmp_no_match = kdmp_non_reply[~kdmp_has_kdmp & ~kdmp_has_kopdes & ~kdmp_has_desa_mp & ~kdmp_has_mbg]
print(f"Rows without any of those anchors (Potential Noise): {len(kdmp_no_match):,}")

print("\nSamples of KDMP potential noise:")
for idx, r in kdmp_no_match.head(10).iterrows():
    c = str(r['content']).replace('\n', ' ')
    print(f"[{r['keyword']}] {c[:140]}...")
