import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

df_yt = pd.read_csv('ScrapeData/scraped_YouTube_Only.csv', low_memory=False)
print(f"Total YouTube rows: {len(df_yt)}")
print(f"Columns: {list(df_yt.columns)}")

# Check empty columns
for col in df_yt.columns:
    nulls = df_yt[col].isna().sum() + (df_yt[col].astype(str).str.strip().isin(['', 'nan', 'None'])).sum()
    print(f"  Col '{col}': {nulls}/{len(df_yt)} null ({nulls/len(df_yt)*100:.1f}%)")

print("\nTopic distribution in YouTube:")
print(df_yt['topic'].value_counts())

print("\nKeywords in YouTube:")
print(f"Total unique keywords: {df_yt['keyword'].nunique()}")
print(df_yt['keyword'].value_counts().head(20))

# Check relevance
for t in df_yt['topic'].unique():
    sub = df_yt[df_yt['topic'] == t]
    print(f"\nSample 3 rows for Topic {t}:")
    for idx, r in sub.head(3).iterrows():
        print(f"  [{r['keyword']}] {repr(str(r['content'])[:80])} | Ch: {r['author']}")
