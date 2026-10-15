import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import re

df_kand = pd.read_csv('ScrapeData/scraped_Threads_Kandidat_Hapus.csv', low_memory=False)
non_reply_kand = df_kand[df_kand['alasan_rekomendasi_hapus'].str.contains('Algoritmik', case=False)]

PATTERNS = {
    'MBG': re.compile(
        r'(?:'
        r'makan(?:an)?\s+beracun(?:\s+gratis)?|'
        r'makan(?:an)?\s+gratis\s+beracun|'
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
        r'makan(?:an)?.{0,20}bergizi|'
        r'makan(?:an)?.{0,20}gratis|'
        r'makan(?:an)?.{0,20}siang|'
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
        r'gizi.{0,25}(?:anak|siswa|murid|sekolah|bumil|ibu|hamil)|'
        r'(?:prabowo|gibran).{0,40}(?:makan|gizi|susu)'
        r')',
        re.IGNORECASE
    ),
    'KDMP': re.compile(
        r'(?:'
        r'\bkdmp\b|koperasi\s+desa|desa\s+merah\s+putih|koperasi\s+merah\s+putih|'
        r'desa\s+mandiri\s+pangan|\bkoperasi\b|dana\s+desa|kopdes|bumdes|'
        r'koperasi\s+umkm'
        r')',
        re.IGNORECASE
    ),
    'Sekolah_Rakyat': re.compile(
        r'(?:'
        r'sekolah\s+rakyat|sekolah\s+gratis\s+rakyat|sekolah.{0,20}gratis|'
        r'pendidikan\s+sekolah\s+rakyat|pendidikan.{0,20}rakyat|'
        r'kemendikdasmen|sekolah\s+negeri\s+rakyat'
        r')',
        re.IGNORECASE
    )
}

combined_pattern = re.compile(f"({PATTERNS['MBG'].pattern})|({PATTERNS['KDMP'].pattern})|({PATTERNS['Sekolah_Rakyat'].pattern})", re.IGNORECASE)

content = non_reply_kand['content'].fillna('').astype(str)
matches = content.str.contains(combined_pattern)
print(f"Total non-reply in kandidat matching ANY topic pattern: {matches.sum()} / {len(non_reply_kand)}")
