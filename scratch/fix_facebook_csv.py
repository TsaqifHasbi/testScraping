import pandas as pd
import re
import os
import shutil

csv_path = 'c:/Users/Asus/OneDrive/Documents/Project_Streamlit/cobaAPI/ScrapeData/scraped_Facebook_Only.csv'
backup_path = 'c:/Users/Asus/OneDrive/Documents/Project_Streamlit/cobaAPI/ScrapeData/scraped_Facebook_Only_BEFORE_CLEAN.csv'

# Backup first
if not os.path.exists(backup_path):
    shutil.copy2(csv_path, backup_path)
    print(f"[BACKUP] Saved backup to {backup_path}")

df = pd.read_csv(csv_path, encoding='utf-8-sig')
print(f"Total rows before: {len(df)}")

def clean_author(row):
    author = str(row['author']) if pd.notna(row['author']) else ''
    content = str(row['content']) if pd.notna(row['content']) else ''

    # 1. Kasus Online status indicator / Active
    if 'Online status indicator' in author or 'Active' in author or 'aktif' in author.lower():
        # Cek apakah nama media/halaman ada di awal konten (misal Radio ANDIKA)
        m_radio = re.match(r'^(Radio\s+[A-Za-z0-9_]+)', content)
        if m_radio:
            return m_radio.group(1)
        m_news = re.match(r'^([A-Z\s]{3,25})\s*[-–—:]\s*', content)
        if m_news:
            candidate = m_news.group(1).strip()
            if candidate not in ['BGN', 'MBG', 'IKN', 'PROGRAM', 'PRESIDEN']:
                return candidate
        return "Facebook_User"

    # 2. Kasus Obfuscated Sponsored text (\u034f)
    if '\u034f' in author or author.count('\u034f') > 0:
        return "Facebook_User"

    # 3. Bersihkan newline dan spasi liar
    author = re.sub(r'[\r\n\t]+', ' ', author)
    author = re.sub(r'\s+', ' ', author).strip()

    # 4. Filter junk UI text
    if re.search(r'^(?:see more|lihat selengkapnya|sponsored|bersponsor)$', author, re.IGNORECASE):
        return "Facebook_User"

    if len(author) < 2:
        return "Facebook_User"

    return author

df['author'] = df.apply(clean_author, axis=1)

# Pastikan SEMUA kolom bersih dari newline liar
for col in df.columns:
    df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[\r\n]+', ' ', x).strip() if x != 'nan' else '')

# Validasi
active_count = df['author'].str.contains('Online status indicator|Active', case=False).sum()
newline_count = sum(df[col].str.contains(r'[\r\n]').sum() for col in df.columns)
print(f"Rows with Active in author after: {active_count}")
print(f"Total newlines in any column after: {newline_count}")
print(f"Total rows after: {len(df)}")

# Simpan ke CSV
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print("[OK] Successfully saved cleaned CSV!")
