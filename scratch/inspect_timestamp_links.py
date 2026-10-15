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
    if (!feed) return [];
    
    let items = Array.from(feed.children);
    let out = [];
    
    // Check first 3 posts
    items.slice(0, 3).forEach((item, idx) => {
        // Find timestamp link: usually near author name in header
        // Often has aria-label with date or span with timestamp or role="link"
        let allA = Array.from(item.querySelectorAll('a'));
        let linkData = allA.map(a => {
            return {
                attrHref: a.getAttribute('href'),
                propHref: a.href,
                text: (a.innerText || '').trim(),
                aria: a.getAttribute('aria-label') || '',
                parentText: (a.parentElement ? a.parentElement.innerText : '').trim().substring(0, 80)
            };
        });
        out.push({ idx: idx, links: linkData });
    });
    return out;
    """
    res = driver.execute_script(js)
    for r in res:
        print(f"\n================ POST {r['idx']} ================")
        for l in r['links']:
            print("ATTR:", l['attrHref'][:80])
            print("PROP:", l['propHref'][:80])
            print("TXT :", l['text'][:40], "| ARIA:", l['aria'][:40])
            print("PARENT:", l['parentText'][:50])
            print("---")
finally:
    driver.quit()
