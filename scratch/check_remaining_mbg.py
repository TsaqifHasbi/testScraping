import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re
from collections import Counter

df_kandidat = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
reply_pat = re.compile(
    r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)',
    re.IGNORECASE
)
is_reply_kandidat = df_kandidat['content'].fillna('').astype(str).str.contains(reply_pat)

mbg_sarcasm_and_variations = re.compile(
    r'(?:'
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

mbg_mask = (df_kandidat['topic'] == 'MBG')
mbg_kandidat = df_kandidat[mbg_mask]
mbg_non_reply = mbg_kandidat[~is_reply_kandidat[mbg_mask]]

mbg_sarcasm_matches = mbg_non_reply['content'].fillna('').astype(str).str.contains(mbg_sarcasm_and_variations)

unmatched = mbg_non_reply[~mbg_sarcasm_matches]
print(f"Total remaining unmatched MBG non-reply: {len(unmatched)}")

words = []
for text in unmatched['content'].fillna('').astype(str):
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    words.extend(tokens)

stopwords = set(['dan', 'yang', 'ini', 'itu', 'ada', 'dari', 'untuk', 'dengan', 'saya', 'bisa', 'dia', 'mereka', 'akan', 'juga', 'sudah', 'karena', 'pada', 'atau', 'tapi', 'tidak', 'lagi', 'oleh', 'kami', 'kita', 'kalo', 'kalau', 'aja', 'jadi', 'nya', 'aku', 'kamu', 'banget', 'banyak', 'lebih', 'mau', 'sama', 'buat', 'dalam', 'udah', 'gak', 'bukan', 'harus', 'masih', 'kok', 'gitu', 'tau', 'kan', 'sih', 'apa', 'terus', 'bgt', 'dong', 'biar', 'gimana', 'kalian', 'mana', 'cuma', 'seperti', 'orang', 'punya', 'hari', 'saat'])
filtered = [w for w in words if w not in stopwords]
counter = Counter(filtered)
print('Top 30 words in remaining unmatched:')
for w, c in counter.most_common(30):
    print(f'{w:15}: {c}')
