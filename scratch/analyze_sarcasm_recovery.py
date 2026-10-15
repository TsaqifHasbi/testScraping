import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

# Load candidate file
df_kandidat = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
print(f"Total rows in kandidat hapus: {len(df_kandidat):,}")

# Reply detector
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)',
    re.IGNORECASE
)
is_reply_kandidat = df_kandidat['content'].fillna('').astype(str).str.contains(reply_pat)
print(f"Replies in kandidat hapus: {is_reply_kandidat.sum():,}")
print(f"Non-replies in kandidat hapus: {(~is_reply_kandidat).sum():,}")

# Expanded patterns for MBG (Sarcasm, Satire, Critical, & Variations)
mbg_sarcasm_and_variations = re.compile(
    r'(?:'
    # Sarcastic terms
    r'makan(?:an)?\s+beracun(?:\s+gratis)?|'
    r'makan(?:an)?\s+basi(?:\s+gratis)?|'
    r'makan(?:an)?\s+gratis\s+basi|'
    r'makan\s+siang\s+beracun|'
    r'bagi(?:-bagi)?\s+racun|'
    r'ompreng(?:an)?|'
    r'susu\s+(?:basi|ikan|gratis|uht)|'
    r'janji\s+(?:manis\s+)?makan|'
    r'menu\s+(?:10\s*rb|15\s*rb|sepuluh\s*ribu|lima\s*belas\s*ribu)|'
    r'(?:korban|kasus|dugaan|insiden)?\s*(?:keracunan|beracun).{0,50}(?:makan|siswa|murid|anak|sekolah|massal|program|gratis|uji\s*coba)|'
    r'(?:siswa|murid|anak|sekolah).{0,50}(?:keracunan|beracun)|'
    # Genuine MBG variations missed by strict regex
    r'makanan\s+bergizi\s+gratis|'
    r'makan(?:an)?\s+gratis\s+bergizi|'
    r'makan(?:an)?\s+bergizi|'
    r'makan(?:an)?\s+gratis|'
    r'makan\s+siang|'
    r'\bmbg\b|'
    r'badan\s+gizi\s+nasional|\bbgn\b|'
    r'dadan\s+hindayana|'
    r'\bsppg\b|satuan\s+pelayanan\s+(?:pemenuhan\s+)?gizi|'
    r'dapur\s+(?:gizi|mbg|sehat|komunal|umum)|'
    r'menu\s+mbg|anggaran\s+(?:mbg|makan|gizi)|'
    r'program\s+makan(?:an)?|'
    r'proyek\s+makan(?:an)?|'
    r'uji\s+coba\s+makan|'
    r'vendor\s+makan|katering\s+makan|'
    r'(?:prabowo|gibran).{0,40}(?:makan|gizi|susu)'
    r')',
    re.IGNORECASE
)

# Apply to MBG topic
mbg_mask = (df_kandidat['topic'] == 'MBG')
mbg_kandidat = df_kandidat[mbg_mask]
mbg_non_reply = mbg_kandidat[~is_reply_kandidat[mbg_mask]]

mbg_sarcasm_matches = mbg_non_reply['content'].fillna('').astype(str).str.contains(mbg_sarcasm_and_variations)
print(f"\nMBG non-reply matching sarcasm/variations in kandidat: {mbg_sarcasm_matches.sum():,} / {len(mbg_non_reply):,}")

# What if reply contains sarcasm? User says: "tapi kalo ada yang rply atau membalas tetep dibuang aja gausa dimasukin"
mbg_reply = mbg_kandidat[is_reply_kandidat[mbg_mask]]
mbg_reply_sarcasm = mbg_reply['content'].fillna('').astype(str).str.contains(mbg_sarcasm_and_variations)
print(f"MBG reply matching sarcasm/variations in kandidat: {mbg_reply_sarcasm.sum():,} (TETAP DIBUANG SESUAI PERMINTAAN USER)")
