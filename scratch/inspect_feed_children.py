import os
import sys
import time
import urllib.parse

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import undetected_chromedriver as uc

FB_PROFILE_DIR = os.path.join(os.path.expanduser('~'), '.facebook_scraper_profile')

options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')
options.add_argument("--disable-notifications")
options.add_argument('--lang=id-ID,id,en-US,en')
options.add_argument(f'--user-data-dir={FB_PROFILE_DIR}')

driver = uc.Chrome(options=options)
try:
    query = urllib.parse.quote("makan bergizi gratis")
    url = f"https://www.facebook.com/search/posts/?q={query}"
    driver.get(url)
    time.sleep(5)
    
    js = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return { error: "No feed" };
    
    // Direct children of feed or children of container
    let children = Array.from(feed.children);
    
    let items = [];
    children.forEach((c, idx) => {
        let text = (c.innerText || '').trim();
        if (text.length < 30) return;
        
        let allLinks = Array.from(c.querySelectorAll('a[href]')).map(a => a.getAttribute('href'));
        
        // Find buttons inside this post
        let buttons = Array.from(c.querySelectorAll('div[role="button"], span[role="button"], span'))
            .map(b => (b.innerText || '').trim())
            .filter(t => t.length > 0 && t.length < 40);
            
        items.push({
            idx: idx,
            textLen: text.length,
            textPreview: text.substring(0, 100).replace(/\\n/g, ' '),
            links: allLinks.slice(0, 8),
            buttons: buttons.slice(0, 10)
        });
    });
    
    return {
        feedChildrenCount: children.length,
        items: items
    };
    """
    res = driver.execute_script(js)
    print("Feed children:", res.get('feedChildrenCount'))
    for it in res.get('items', [])[:4]:
        print(f"\n--- FEED ITEM {it['idx']} ---")
        print("Text preview:", it['textPreview'])
        print("Buttons:", it['buttons'])
        print("Links:")
        for l in it['links']:
            print("  ", l[:100])
finally:
    driver.quit()
