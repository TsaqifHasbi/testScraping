"""
Audit seluruh CSV scraping:
1. Cek urutan keyword vs config
2. Cek korelasi konten dengan keyword / topik
3. Cek data kosong / anomali
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, 'colab_cells')

import pandas as pd
import os
import re
import json
from collections import OrderedDict

# Load config keywords
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

# Flatten keyword order from config
CONFIG_KW_ORDER = []
CONFIG_KW_TOPIC = {}
for topic, kws in TOPICS.items():
    for kw in kws:
        CONFIG_KW_ORDER.append(kw)
        CONFIG_KW_TOPIC[kw] = topic

# Topic core terms for relevance checking
TOPIC_TERMS = {
    'MBG': ['mbg', 'makan bergizi', 'bergizi gratis', 'bgn', 'sppg', 'gizi', 'stunting',
            'keracunan', 'makanan gratis', 'makan gratis', 'pemenuhan gizi', 'menu mbg',
            'satuan pelayanan', 'badan gizi', 'dapur mbg', 'program makan'],
    'KDMP': ['kdmp', 'koperasi desa', 'merah putih', 'koperasi umkm', 'dana desa',
             'pemberdayaan desa', 'kopdes', 'bumdes', 'koperasi rakyat'],
    'Sekolah_Rakyat': ['sekolah rakyat', 'sekolah gratis', 'pendidikan rakyat',
                       'kemendikdasmen', 'sekolah asrama', 'beasiswa sekolah',
                       'pendaftaran sekolah', 'kurikulum sekolah'],
}

results = {}

for platform, fname in FILES.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"\n{'='*60}")
        print(f"[SKIP] {fname} tidak ditemukan.")
        continue

    try:
        df = pd.read_csv(path, encoding='utf-8-sig')
    except Exception:
        df = pd.read_csv(path)

    print(f"\n{'='*70}")
    print(f"📊 {platform} — {fname}")
    print(f"{'='*70}")
    print(f"  Total baris: {len(df)}")
    print(f"  Kolom: {list(df.columns)}")

    # Detect keyword column
    kw_col = 'keyword' if 'keyword' in df.columns else None
    content_col = 'content' if 'content' in df.columns else None
    topic_col = 'topic' if 'topic' in df.columns else None

    if not kw_col:
        print(f"  [WARN] Kolom 'keyword' tidak ditemukan!")
        continue

    # --- 1. CEK URUTAN KEYWORD ---
    csv_kw_order = list(df[kw_col].dropna().unique())
    # Map each keyword to its config index
    config_idx = {kw: i for i, kw in enumerate(CONFIG_KW_ORDER)}

    in_config = [kw for kw in csv_kw_order if kw in config_idx]
    not_in_config = [kw for kw in csv_kw_order if kw not in config_idx]

    if not_in_config:
        print(f"\n  [!] {len(not_in_config)} keyword di CSV TIDAK ADA di config:")
        for kw in not_in_config[:10]:
            print(f"      - '{kw}'")

    # Check if in_config keywords appear in config order
    order_violations = 0
    if len(in_config) >= 2:
        for i in range(len(in_config) - 1):
            idx_a = config_idx[in_config[i]]
            idx_b = config_idx[in_config[i + 1]]
            if idx_b < idx_a:
                order_violations += 1

    if order_violations == 0:
        print(f"  [✅] Urutan keyword: SESUAI config (semua {len(in_config)} keyword berurutan)")
    else:
        print(f"  [⚠️] Urutan keyword: {order_violations} pelanggaran urutan dari {len(in_config)} keyword")

    # --- 2. CEK KORELASI KONTEN vs KEYWORD/TOPIK ---
    if content_col:
        total_checked = 0
        kw_match = 0
        topic_match = 0
        no_match = 0
        no_match_samples = []

        for idx, row in df.iterrows():
            kw = str(row.get(kw_col, '')).lower()
            content = str(row.get(content_col, '')).lower()
            topic = str(row.get(topic_col, '')).strip() if topic_col else ''

            if not content or content == 'nan' or len(content) < 10:
                continue

            total_checked += 1

            # Remove emoji from keyword for matching
            kw_clean = re.sub(r'[^\w\s]', '', kw).strip()

            # Check 1: Does content contain keyword or keyword words?
            found_kw = False
            if kw_clean and kw_clean in content:
                found_kw = True
            else:
                words = [w for w in kw_clean.split() if len(w) >= 3]
                if words:
                    found_kw = sum(1 for w in words if w in content) >= max(1, len(words) // 2)

            if found_kw:
                kw_match += 1
                continue

            # Check 2: Does content match topic terms?
            found_topic = False
            # Determine topic from keyword
            mapped_topic = CONFIG_KW_TOPIC.get(row.get(kw_col, ''), topic)
            terms = TOPIC_TERMS.get(mapped_topic, [])
            if terms:
                found_topic = any(t in content for t in terms)

            if found_topic:
                topic_match += 1
                continue

            # No match at all
            no_match += 1
            if len(no_match_samples) < 5:
                no_match_samples.append({
                    'row': idx,
                    'keyword': row.get(kw_col, ''),
                    'topic': topic,
                    'content_preview': content[:80],
                })

        pct_kw = (kw_match / total_checked * 100) if total_checked else 0
        pct_topic = (topic_match / total_checked * 100) if total_checked else 0
        pct_total = ((kw_match + topic_match) / total_checked * 100) if total_checked else 0
        pct_nomatch = (no_match / total_checked * 100) if total_checked else 0

        print(f"\n  📋 Korelasi Konten vs Keyword/Topik (dari {total_checked} baris berisi konten):")
        print(f"     ✅ Cocok keyword langsung : {kw_match:>6} ({pct_kw:.1f}%)")
        print(f"     ✅ Cocok tema/topik       : {topic_match:>6} ({pct_topic:.1f}%)")
        print(f"     ─────────────────────────────────────────")
        print(f"     ✅ TOTAL RELEVAN          : {kw_match+topic_match:>6} ({pct_total:.1f}%)")
        print(f"     ❌ Tidak cocok sama sekali : {no_match:>6} ({pct_nomatch:.1f}%)")

        if no_match_samples:
            print(f"\n  📌 Contoh konten yang TIDAK cocok keyword/topik:")
            for s in no_match_samples:
                print(f"     Row {s['row']}: KW='{s['keyword']}' | Topic={s['topic']}")
                print(f"       Content: {s['content_preview']}...")

    # --- 3. CEK DATA KOSONG / NULL ---
    null_counts = df.isnull().sum()
    cols_with_null = null_counts[null_counts > 0]
    if len(cols_with_null) > 0:
        print(f"\n  ⚠️ Kolom dengan data kosong:")
        for col, cnt in cols_with_null.items():
            print(f"     {col}: {cnt} baris kosong ({cnt/len(df)*100:.1f}%)")
    else:
        print(f"\n  [✅] Tidak ada kolom dengan data kosong/null.")

    # --- 4. DISTRIBUSI TOPIK ---
    if topic_col and topic_col in df.columns:
        print(f"\n  📊 Distribusi Topik:")
        for t, cnt in df[topic_col].value_counts().items():
            print(f"     {t}: {cnt} baris")

    # --- 5. KEYWORD COVERAGE ---
    kw_counts = df[kw_col].value_counts()
    missing_kws = [kw for kw in CONFIG_KW_ORDER if kw not in set(df[kw_col].dropna().unique())]
    print(f"\n  📊 Keyword Coverage:")
    print(f"     Config total    : {len(CONFIG_KW_ORDER)} keywords")
    print(f"     Ada di CSV      : {len(in_config)} keywords")
    print(f"     Belum ada       : {len(missing_kws)} keywords")
    if missing_kws:
        # Breakdown by topic
        from collections import Counter
        miss_topics = Counter(CONFIG_KW_TOPIC[k] for k in missing_kws if k in CONFIG_KW_TOPIC)
        for t, c in miss_topics.items():
            total_t = len(TOPICS[t])
            print(f"       {t}: {c}/{total_t} belum ada")

    results[platform] = {
        'rows': len(df),
        'keywords_present': len(in_config),
        'keywords_missing': len(missing_kws),
        'order_ok': order_violations == 0,
        'relevance_pct': pct_total if content_col else -1,
    }

# === RINGKASAN ===
print(f"\n\n{'='*70}")
print(f"📊 RINGKASAN AUDIT SELURUH PLATFORM")
print(f"{'='*70}")
print(f"{'Platform':<12} {'Baris':>8} {'KW Ada':>7} {'KW Miss':>8} {'Urutan':>8} {'Relevansi':>10}")
print(f"{'-'*12} {'-'*8} {'-'*7} {'-'*8} {'-'*8} {'-'*10}")
for p, r in results.items():
    order_str = '✅' if r['order_ok'] else '⚠️'
    rel_str = f"{r['relevance_pct']:.1f}%" if r['relevance_pct'] >= 0 else 'N/A'
    print(f"{p:<12} {r['rows']:>8} {r['keywords_present']:>7} {r['keywords_missing']:>8} {order_str:>8} {rel_str:>10}")
