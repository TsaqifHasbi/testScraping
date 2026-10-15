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
    
    items.slice(0, 3).forEach((item, idx) => {
        let links = Array.from(item.querySelectorAll('a[href]')).map(a => ({
            href: a.getAttribute('href'),
            text: (a.innerText || '').trim(),
            aria: a.getAttribute('aria-label') || '',
            role: a.getAttribute('role') || '',
            outer: a.outerHTML.substring(0, 200)
        }));
        
        // Let's also check all elements with text "Lihat selengkapnya" or "See more"
        let seeMores = Array.from(item.querySelectorAll('*')).filter(el => {
            let t = (el.innerText || '').trim();
            return /lihat selengkapnya|see more/i.test(t);
        }).map(el => ({
            tag: el.tagName,
            text: el.innerText.trim(),
            role: el.getAttribute('role'),
            classes: el.className
        }));
        
        out.push({
            idx: idx,
            links: links,
            seeMores: seeMores
        });
    });
    return out;
    """
    res = driver.execute_script(js)
    for r in res:
        print(f"\n================ POST {r['idx']} ================")
        print("SeeMores in this post:")
        for sm in r['seeMores']:
            print("  ", sm)
        print("Links in this post:")
        for l in r['links']:
            print("   HREF:", l['href'][:90])
            print("   TXT :", l['text'][:40], "| ARIA:", l['aria'][:40], "| ROLE:", l['role'])
            print("   HTML:", l['outer'][:120])
            print("   -----------------")
finally:
    driver.quit()
