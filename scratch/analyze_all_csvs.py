import os, sys
import io

# Force stdout/stderr to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

# Import config
sys.path.insert(0, os.path.abspath('.'))
from colab_cells.cell_02_config import TOPICS

files = {
    'Facebook': 'ScrapeData/scraped_Facebook_Only.csv',
    'Instagram': 'ScrapeData/scraped_Instagram_Only.csv',
    'News': 'ScrapeData/scraped_News_Only.csv',
    'Threads': 'ScrapeData/scraped_Threads_Only.csv',
    'TikTok': 'ScrapeData/scraped_TikTok_Only.csv',
    'Twitter': 'ScrapeData/scraped_Twitter_Only.csv',
    'YouTube': 'ScrapeData/scraped_YouTube_Only.csv'
}

all_cfg_kws = []
for t, kws in TOPICS.items():
    for kw in kws:
        all_cfg_kws.append((t, kw))

configured_kw_list = [kw for t, kw in all_cfg_kws]
print(f"Total configured keywords in cell_02_config: {len(configured_kw_list)}")

for name, path in files.items():
    print("=" * 60)
    print(f"ANALISIS: {name} ({path})")
    if not os.path.exists(path):
        print("FILE NOT FOUND")
        continue
    
    df = pd.read_csv(path, low_memory=False)
    print(f"Total Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # 1. Empty columns (100% null or whitespace)
    empty_cols = []
    for c in df.columns:
        s = df[c].dropna().astype(str).str.strip()
        if len(s) == 0 or (s == '').all() or (s == 'nan').all() or (s == 'None').all():
            empty_cols.append(c)
    print(f"Empty columns (100% empty): {empty_cols}")

    # Null counts per column
    null_info = {}
    for c in df.columns:
        n_null = df[c].isna().sum() + (df[c].astype(str).str.strip().isin(['', 'nan', 'None'])).sum()
        if n_null > 0:
            null_info[c] = f"{n_null}/{len(df)} ({n_null/len(df)*100:.1f}%)"
    if null_info:
        print(f"Columns with empty/null values: {null_info}")

    # 2. Check keywords
    if 'keyword' in df.columns:
        # Find unique keywords preserving first appearance order
        seen_order = []
        for kw in df['keyword'].dropna():
            if not seen_order or seen_order[-1] != kw:
                if kw not in seen_order:
                    seen_order.append(kw)
        
        csv_unique_kws = set(df['keyword'].dropna().unique())
        print(f"Total unique keywords in CSV: {len(csv_unique_kws)}")
        
        # Missing & extra
        missing = [kw for kw in configured_kw_list if kw not in csv_unique_kws]
        extra = [kw for kw in csv_unique_kws if kw not in configured_kw_list]
        print(f"Keywords from config missing in CSV: {len(missing)}")
        if missing:
            print(f"  Missing examples: {missing[:10]}")
        if extra:
            print(f"  Extra keywords not in config ({len(extra)}): {extra[:10]}")
            
        # Check order
        pos_in_cfg = [configured_kw_list.index(kw) for kw in seen_order if kw in configured_kw_list]
        is_sorted = (pos_in_cfg == sorted(pos_in_cfg))
        print(f"Keyword order matches config sequence? {is_sorted}")
        if not is_sorted:
            inversions = 0
            for i in range(len(pos_in_cfg)-1):
                if pos_in_cfg[i] > pos_in_cfg[i+1]:
                    if inversions < 5:
                        print(f"  Order discrepancy: '{seen_order[i]}' (index {pos_in_cfg[i]}) appeared before '{seen_order[i+1]}' (index {pos_in_cfg[i+1]})")
                    inversions += 1
            print(f"  Total ordering discrepancies: {inversions}")
    print()
