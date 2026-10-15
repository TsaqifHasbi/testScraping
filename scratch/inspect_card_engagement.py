import os
import sys
import time
import urllib.parse
import json

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
    if (!feed) return [];
    
    return Array.from(feed.children).slice(0, 4).map((card, idx) => {
        let arias = Array.from(card.querySelectorAll('*[aria-label]')).map(el => el.getAttribute('aria-label'));
        let btnTexts = Array.from(card.querySelectorAll('div[role="button"], span, div'))
            .map(e => (e.innerText || '').trim())
            .filter(t => /(?:komentar|comments?|shares?|dibagikan|\\d+\\s*(?:rb|k|jt)?)/i.test(t) && t.length < 30);
            
        return {
            idx: idx,
            arias: arias.filter(a => /(?:suka|like|komentar|comment|bagikan|share|\\d+)/i.test(a)),
            btnTexts: [...new Set(btnTexts)].slice(0, 10)
        };
    });
    """
    res = driver.execute_script(js)
    for r in res:
        print(f"\n--- CARD {r['idx']} ---")
        print("Arias   :", r['arias'])
        print("BtnTexts:", [t.replace('\u034f', '') for t in r['btnTexts']])
finally:
    driver.quit()
