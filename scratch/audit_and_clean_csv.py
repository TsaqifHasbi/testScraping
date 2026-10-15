"""
Audit Ulang Seluruh CSV + Clean Kolom 100% Kosong
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, 'colab_cells')

import pandas as pd
import os
import re
from cell_02_config import TOPICS

BASE = 'ScrapeData'

FILES = {
    'Facebook':  'scraped_Facebook_Only.csv',
    'Instagram': 'scraped_Instagram_Only.csv',
    'News':      'scraped_News_Only.csv',
    'Threads':   'scraped_Threads_Only.csv',
    'TikTok':    'scraped_TikTok_Only.csv',
    'Twitter':   'scraped_Twitter_Only.csv',
    'YouTube':   'scraped_YouTube_Only.csv',
}

# 1. Flatten keyword order from config
CONFIG_KW_ORDER = []
CONFIG_KW_TOPIC = {}
for topic, kws in TOPICS.items():
    for kw in kws:
        CONFIG_KW_ORDER.append(kw)
        CONFIG_KW_TOPIC[kw] = topic

config_idx = {kw: i for i, kw in enumerate(CONFIG_KW_ORDER)}

# Topic core terms for relevance checking
TOPIC_TERMS = {
    'MBG': [
        'mbg', 'makan bergizi', 'bergizi gratis', 'bgn', 'sppg', 'gizi', 'stunting',
        'keracunan', 'makanan gratis', 'makan gratis', 'pemenuhan gizi', 'menu mbg',
        'satuan pelayanan', 'badan gizi', 'dapur mbg', 'program makan', 'dadan hindayana',
        'sudaryono', 'uji coba mbg', 'sarapan gratis', 'dapur sehat'
    ],
    'KDMP': [
        'kdmp', 'koperasi desa', 'merah putih', 'koperasi umkm', 'dana desa',
        'pemberdayaan desa', 'kopdes', 'bumdes', 'koperasi rakyat', 'koperasi'
    ],
    'Sekolah_Rakyat': [
        'sekolah rakyat', 'sekolah gratis', 'pendidikan rakyat',
        'kemendikdasmen', 'sekolah asrama', 'beasiswa sekolah',
        'pendaftaran sekolah', 'kurikulum sekolah', 'muammar', 'sekolah vokasi'
    ],
}

audit_summary = {}

for platform, fname in FILES.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"\n[SKIP] {fname} tidak ditemukan.")
        continue

    # Load CSV
    try:
        df = pd.read_csv(path, encoding='utf-8-sig', low_memory=False)
    except Exception:
        df = pd.read_csv(path, low_memory=False)

    print(f"\n{'='*75}")
    print(f"📊 PLATFORM: {platform} ({fname})")
    print(f"{'='*75}")
    print(f"  Total Data : {len(df):,} baris")
    print(f"  Kolom Asli : {list(df.columns)}")

    # ----------------------------------------------------
    # 1. HAPUS KOLOM YANG 100% KOSONG
    # ----------------------------------------------------
    cols_dropped = []
    for col in list(df.columns):
        s = df[col]
        # Kosong jika null atau string kosong atau 'nan'
        is_empty = s.isna() | (s.astype(str).str.strip().isin(['', 'nan', 'NaN', 'None', '<NA>']))
        if is_empty.all():
            cols_dropped.append(col)
            df.drop(columns=[col], inplace=True)

    if cols_dropped:
        print(f"  🗑️  KOLOM 100% KOSONG DIHAPUS: {cols_dropped}")
        # Simpan kembali CSV
        df.to_csv(path, index=False, encoding='utf-8-sig')
        print(f"  💾 Berhasil update file tanpa kolom kosong. Kolom baru: {list(df.columns)}")
    else:
        print(f"  ✅ Tidak ada kolom yang 100% kosong.")

    # ----------------------------------------------------
    # 2. CEK URUTAN KEYWORD
    # ----------------------------------------------------
    kw_col = 'keyword' if 'keyword' in df.columns else None
    content_col = 'content' if 'content' in df.columns else None
    topic_col = 'topic' if 'topic' in df.columns else None

    if not kw_col:
        print("  ⚠️ Kolom 'keyword' tidak ditemukan!")
        continue

    # Urutan kemunculan unik di CSV
    csv_kws = []
    seen = set()
    for kw in df[kw_col].dropna():
        if kw not in seen:
            seen.add(kw)
            csv_kws.append(kw)

    in_config_kws = [k for k in csv_kws if k in config_idx]
    not_in_config_kws = [k for k in csv_kws if k not in config_idx]

    order_ok = True
    order_inversions = []
    for i in range(len(in_config_kws) - 1):
        curr_k = in_config_kws[i]
        next_k = in_config_kws[i+1]
        idx_curr = config_idx[curr_k]
        idx_next = config_idx[next_k]
        if idx_next < idx_curr:
            order_ok = False
            order_inversions.append((curr_k, idx_curr, next_k, idx_next))

    print(f"\n  📌 Status Urutan Keyword:")
    print(f"     - Keyword Unik di CSV : {len(csv_kws)} keyword")
    print(f"     - Ada di Config       : {len(in_config_kws)}/{len(CONFIG_KW_ORDER)}")
    if not_in_config_kws:
        print(f"     - Di luar Config      : {len(not_in_config_kws)} ({not_in_config_kws[:5]}...)")

    if order_ok:
        print(f"     - Status Urutan       : ✅ SESUAI DENGAN CONFIG (100% urut)")
    else:
        print(f"     - Status Urutan       : ⚠️ ADA {len(order_inversions)} PELANGGARAN URUTAN:")
        for c_k, c_i, n_k, n_i in order_inversions[:5]:
            print(f"       * Urutan terbalik: '{c_k}' (pos #{c_i}) muncul SEBELUM '{n_k}' (pos #{n_i})")

    # ----------------------------------------------------
    # 3. CEK KORELASI KONTEN DENGAN KEYWORD / TOPIK
    # ----------------------------------------------------
    total_valid = 0
    direct_match = 0
    topic_match = 0
    off_topic = 0
    off_samples = []

    if content_col:
        # Pre-process contents
        contents = df[content_col].fillna('').astype(str)
        keywords = df[kw_col].fillna('').astype(str)
        topics = df[topic_col].fillna('').astype(str) if topic_col else pd.Series(['']*len(df))

        # Iterasi efisien dengan zip
        for idx, (c_raw, kw_raw, top_raw) in enumerate(zip(contents, keywords, topics)):
            c = str(c_raw).lower().strip()
            if not c or c in ['nan', 'none', 'null', ''] or len(c) < 5:
                continue

            total_valid += 1
            kw = str(kw_raw).lower().strip()
            # Bersihkan emoji dari keyword untuk checking
            kw_clean = re.sub(r'[^\w\s]', '', kw).strip()

            # A. Cek kecocokan langsung keyword
            matched_direct = False
            if kw_clean and kw_clean in c:
                matched_direct = True
            else:
                # Cek potongan kata keyword (jika frasa >= 2 kata)
                words = [w for w in kw_clean.split() if len(w) >= 3]
                if len(words) >= 2:
                    matched_words = sum(1 for w in words if w in c)
                    if matched_words >= len(words) * 0.7:  # minimal 70% kata cocok
                        matched_direct = True

            if matched_direct:
                direct_match += 1
                continue

            # B. Cek kecocokan tema/objek (jika keyword tidak persis muncul)
            matched_theme = False
            # Tentukan topik dari config atau data
            active_topic = CONFIG_KW_TOPIC.get(kw_raw, top_raw.strip())
            terms = TOPIC_TERMS.get(active_topic, [])
            if any(t in c for t in terms):
                matched_theme = True

            if matched_theme:
                topic_match += 1
                continue

            # C. Tidak cocok sama sekali
            off_topic += 1
            if len(off_samples) < 3:
                off_samples.append({
                    'row': idx,
                    'kw': kw_raw,
                    'topic': active_topic,
                    'snippet': (c_raw[:100] + '...') if len(c_raw) > 100 else c_raw
                })

        pct_direct = (direct_match / total_valid * 100) if total_valid else 0
        pct_topic = (topic_match / total_valid * 100) if total_valid else 0
        pct_relevant = ((direct_match + topic_match) / total_valid * 100) if total_valid else 0
        pct_off = (off_topic / total_valid * 100) if total_valid else 0

        print(f"\n  🎯 Korelasi Konten vs Keyword & Topik ({total_valid:,} data valid):")
        print(f"     ✅ Cocok Keyword Langsung : {direct_match:>8,} ({pct_direct:.1f}%)")
        print(f"     ✅ Cocok Tema / Objek     : {topic_match:>8,} ({pct_topic:.1f}%)")
        print(f"     🌟 TOTAL RELEVAN          : {direct_match + topic_match:>8,} ({pct_relevant:.1f}%)")
        print(f"     ❌ Tidak Terkorelasi      : {off_topic:>8,} ({pct_off:.1f}%)")

        if off_samples:
            print(f"\n     Contoh Konten Tidak Terkorelasi:")
            for s in off_samples:
                print(f"       [Baris {s['row']}] KW='{s['kw']}' (Topik: {s['topic']})")
                print(f"         Konten: \"{s['snippet']}\"")

    # ----------------------------------------------------
    # 4. DISTRIBUSI TOPIK & KEYWORD MISSING
    # ----------------------------------------------------
    print(f"\n  📈 Distribusi Topik Saat Ini:")
    if topic_col:
        for t, cnt in df[topic_col].value_counts().items():
            print(f"     - {t:<15}: {cnt:>7,} baris")

    missing = [k for k in CONFIG_KW_ORDER if k not in seen]
    print(f"\n  🔍 Keyword Missing ({len(missing)} belum ada):")
    if missing:
        for t in TOPICS.keys():
            t_missing = [k for k in missing if CONFIG_KW_TOPIC.get(k) == t]
            print(f"     - {t:<15}: {len(t_missing)}/{len(TOPICS[t])} belum di-scrape")
    else:
        print("     - Semua 139 keyword sudah lengkap!")

    audit_summary[platform] = {
        'rows': len(df),
        'cols_dropped': cols_dropped,
        'kw_present': len(in_config_kws),
        'kw_missing': len(missing),
        'order_ok': order_ok,
        'order_inversions': len(order_inversions),
        'relevance_pct': pct_relevant if content_col else -1,
        'off_topic_pct': pct_off if content_col else -1,
    }

# ----------------------------------------------------
# RINGKASAN AKHIR
# ----------------------------------------------------
print(f"\n\n{'='*80}")
print("📋 RINGKASAN AKHIR AUDIT & CLEANING SELURUH PLATFORM")
print(f"{'='*80}")
print(f"{'Platform':<12} {'Total Baris':>12} {'Kolom Drop':>12} {'KW Ada/Total':>14} {'Urutan':>10} {'Relevansi':>12}")
print(f"{'-'*12} {'-'*12} {'-'*12} {'-'*14} {'-'*10} {'-'*12}")
for p, s in audit_summary.items():
    drop_str = ', '.join(s['cols_dropped']) if s['cols_dropped'] else '-'
    ord_str = '✅ Sesuai' if s['order_ok'] else f"⚠️ ({s['order_inversions']})"
    rel_str = f"{s['relevance_pct']:.1f}%" if s['relevance_pct'] >= 0 else 'N/A'
    kw_str = f"{s['kw_present']}/{len(CONFIG_KW_ORDER)}"
    print(f"{p:<12} {s['rows']:>12,} {drop_str:>12} {kw_str:>14} {ord_str:>10} {rel_str:>12}")
