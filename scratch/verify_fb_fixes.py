import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.append(r'c:\Users\Asus\OneDrive\Documents\Project_Streamlit\cobaAPI\colab_cells')
from cell_09_facebook import scrape_facebook, FB_DRIVER

try:
    print("Testing scrape_facebook with new fixes...")
    posts = scrape_facebook("makan bergizi gratis", max_results=5)
    print(f"\n[HASIL TEST] Didapatkan {len(posts)} posts:")
    for i, p in enumerate(posts):
        print(f"\n--- POST {i+1} ---")
        print("Author :", p['author'])
        print("URL    :", p['url'])
        print("Likes  :", p['likes'], "| Comments:", p['comments'], "| Shares:", p['shares'])
        print("Content Len:", len(p['content']))
        print("Ends with ellipsis?:", p['content'].endswith('…') or p['content'].endswith('...'))
        print("Content Snippet:", p['content'][:120])
        print("Content End    :", p['content'][-80:])
        
        # VALIDATIONS
        assert '/stories/' not in p['url'], f"FAIL: URL contains story: {p['url']}"
        assert not p['url'].endswith('.com/groups/1179153730937334/'), f"FAIL: URL is root community: {p['url']}"
        print("[V] Valid post permalink!")
finally:
    if FB_DRIVER:
        try:
            FB_DRIVER.quit()
        except:
            pass
