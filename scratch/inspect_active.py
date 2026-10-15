import pandas as pd

df = pd.read_csv('c:/Users/Asus/OneDrive/Documents/Project_Streamlit/cobaAPI/ScrapeData/scraped_Facebook_Only.csv')
print('Total rows:', len(df))
print('Columns:', df.columns.tolist())

# Check where 'active' appears
for col in df.columns:
    if df[col].dtype == object:
        matches = df[df[col].astype(str).str.contains('active', case=False, na=False)]
        print(f'Column {col} containing active: {len(matches)} rows')

# Look at rows where author or content has 'active'
active_authors = df[df['author'].astype(str).str.contains('active', case=False, na=False)]
print('\nSample active authors (first 10):')
for idx, row in active_authors.head(10).iterrows():
    print(f"Row {idx}: author='{row['author']}' | content='{str(row['content'])[:60]}' | url='{row['url']}'")

# Look at rows where content starts with 'active'
active_content = df[df['content'].astype(str).str.startswith('Active', na=False) | df['content'].astype(str).str.startswith('active', na=False)]
print('\nSample content starting with active (first 10):')
for idx, row in active_content.head(10).iterrows():
    print(f"Row {idx}: author='{row['author']}' | content='{str(row['content'])[:80]}' | url='{row['url']}'")

# Check rows where author is literally 'Active' or starts with 'Active'
print('\nAuthors starting with Active:')
sw_active = df[df['author'].astype(str).str.startswith('Active', na=False)]
print(f'Count: {len(sw_active)}')
for idx, row in sw_active.head(10).iterrows():
    print(f"Row {idx}: author='{row['author']}' | content='{str(row['content'])[:60]}'")

# Check empty/null/short rows
print('\nEmpty or short content (< 30 chars):', len(df[df['content'].astype(str).str.len() < 30]))
print('Empty or short authors (< 3 chars):', len(df[df['author'].astype(str).str.len() < 3]))
print('Null values per column:')
print(df.isnull().sum())
