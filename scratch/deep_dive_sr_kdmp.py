import sys
import io
import pandas as pd
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors='replace')

df = pd.read_csv('ScrapeData/scraped_Threads_Only_BEFORE_FILTER.csv', low_memory=False)

for topic_name in ['Sekolah_Rakyat', 'KDMP']:
    print("=" * 80)
    print(f"DEEP DIVE: TOPIC {topic_name}")
    print("=" * 80)
    sub = df[df['topic'] == topic_name].copy().reset_index(drop=True)
    content = sub['content'].fillna('').astype(str)
    
    # 1. Reply detection
    is_reply = content.str.contains(
        r'(?:^|[\r\n\s])(?:Membalas\s+@|Replying\s+to\s+@|Balasan\s+pada\s+postingan|Balasan\s+untuk\s+@)|(?:^@[\w\.-]+\s+)',
        re.I
    )
    print(f"Total rows: {len(sub):,}")
    print(f"  - Replies: {is_reply.sum():,} ({is_reply.sum()/len(sub)*100:.1f}%)")
    print(f"  - Non-Replies: {(~is_reply).sum():,} ({(~is_reply).sum()/len(sub)*100:.1f}%)")
    
    non_reply = sub[~is_reply].copy().reset_index(drop=True)
    nr_content = non_reply['content'].fillna('').astype(str)
    
    if topic_name == 'Sekolah_Rakyat':
        # Analyze Sekolah Rakyat content
        pat_sr = re.compile(r'sekolah\s+rakyat|pendidikan\s+rakyat|sekolah\s+negeri\s+rakyat', re.I)
        pat_sekolah_gratis = re.compile(r'sekolah\s+gratis|pendidikan\s+gratis|biaya\s+sekolah|sekolah\s+berasrama', re.I)
        pat_kemendik = re.compile(r'kemendikdasmen|mendikdasmen|muhammadiyah|kurikulum|guru\s+honorer', re.I)
        pat_mbg_crossover = re.compile(r'\bmbg\b|makan\s+(?:bergizi|siang|gratis)|bgn\b|sppg\b', re.I)
        
        has_sr = nr_content.str.contains(pat_sr)
        has_gratis = nr_content.str.contains(pat_sekolah_gratis)
        has_kemendik = nr_content.str.contains(pat_kemendik)
        has_mbg = nr_content.str.contains(pat_mbg_crossover)
        
        has_any = has_sr | has_gratis | has_kemendik | has_mbg
        
        print(f"\nBreakdown Non-Reply Sekolah_Rakyat ({len(non_reply):,} rows):")
        print(f"  - Menyebut 'sekolah rakyat': {has_sr.sum():,} ({has_sr.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Menyebut 'sekolah gratis / pendidikan gratis / asrama': {has_gratis.sum():,} ({has_gratis.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Menyebut Kemendikdasmen/Guru/Kurikulum: {has_kemendik.sum():,} ({has_kemendik.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Crossover MBG (membahas MBG di topik SR): {has_mbg.sum():,} ({has_mbg.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Total Ada Relevansi Topik: {has_any.sum():,} ({has_any.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - TOTAL NOISE MURNI (Tanpa keterkaitan): {(~has_any).sum():,} ({(~has_any).sum()/len(non_reply)*100:.1f}%)")
        
        noise_samples = non_reply[~has_any]
        print(f"\nContoh Konten NOISE MURNI di Sekolah_Rakyat:")
        for idx, r in noise_samples.head(15).iterrows():
            c = str(r['content']).replace('\n', ' ')
            print(f"  [{r['keyword']}] {c[:130]}...")
            
    elif topic_name == 'KDMP':
        pat_kdmp = re.compile(r'\bkdmp\b', re.I)
        pat_kop = re.compile(r'koperasi\s+(?:desa|merah\s+putih|unit\s+desa|umkm|simpan\s+pinjam|petani|nelayan)|\bkoperasi\b|kopdes|bumdes', re.I)
        pat_desa_mp = re.compile(r'desa\s+merah\s+putih|desa\s+mandiri|dana\s+desa|pemberdayaan\s+desa', re.I)
        pat_mbg_crossover = re.compile(r'\bmbg\b|makan\s+(?:bergizi|siang|gratis)|bgn\b|sppg\b', re.I)
        
        has_kdmp = nr_content.str.contains(pat_kdmp)
        has_kop = nr_content.str.contains(pat_kop)
        has_desa_mp = nr_content.str.contains(pat_desa_mp)
        has_mbg = nr_content.str.contains(pat_mbg_crossover)
        
        has_any = has_kdmp | has_kop | has_desa_mp | has_mbg
        
        print(f"\nBreakdown Non-Reply KDMP ({len(non_reply):,} rows):")
        print(f"  - Menyebut singkatan 'KDMP': {has_kdmp.sum():,} ({has_kdmp.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Menyebut 'koperasi / kopdes / bumdes': {has_kop.sum():,} ({has_kop.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Menyebut 'desa merah putih / dana desa': {has_desa_mp.sum():,} ({has_desa_mp.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Crossover MBG (membahas MBG/anggaran): {has_mbg.sum():,} ({has_mbg.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - Total Ada Relevansi Topik: {has_any.sum():,} ({has_any.sum()/len(non_reply)*100:.1f}%)")
        print(f"  - TOTAL NOISE MURNI (Tanpa keterkaitan): {(~has_any).sum():,} ({(~has_any).sum()/len(non_reply)*100:.1f}%)")
        
        noise_samples = non_reply[~has_any]
        print(f"\nContoh Konten NOISE MURNI di KDMP:")
        for idx, r in noise_samples.head(15).iterrows():
            c = str(r['content']).replace('\n', ' ')
            print(f"  [{r['keyword']}] {c[:130]}...")
