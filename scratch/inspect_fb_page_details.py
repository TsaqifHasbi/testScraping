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
    // Find all post containers
    // Check role="feed" or div[role="article"]
    let feed = document.querySelector('div[role="feed"]');
    let articles = feed ? feed.querySelectorAll('div[role="article"]') : document.querySelectorAll('div[role="article"]');
    
    let report = [];
    articles.forEach((art, idx) => {
        if (idx > 3) return;
        
        // Find all links
        let links = Array.from(art.querySelectorAll('a[href]')).map(a => ({
            href: a.getAttribute('href'),
            text: (a.innerText || '').trim().substring(0, 50),
            aria: (a.getAttribute('aria-label') || '').substring(0, 50)
        }));
        
        // Find see more
        let seeMores = [];
        art.querySelectorAll('div[role="button"], span[role="button"], span, div').forEach(el => {
            if (el.tagName === 'A' || el.closest('a')) return;
            let t = (el.innerText || '').trim();
            if (/^(?:…|\\.\\.\\.)?\\s*(see more|lihat selengkapnya|selengkapnya)\\s*(?:\\.\\.\\.|…)?$/i.test(t) ||
                t === 'Lihat selengkapnya' || t === 'See more') {
                seeMores.push({
                    tag: el.tagName,
                    role: el.getAttribute('role'),
                    text: t,
                    outerHTML: el.outerHTML.substring(0, 150)
                });
            }
        });
        
        // Find content divs
        let contentDivs = Array.from(art.querySelectorAll('div[dir="auto"]')).map(d => (d.innerText || '').trim()).filter(t => t.length > 20);
        
        report.push({
            idx: idx,
            links: links,
            seeMores: seeMores,
            contentCount: contentDivs.length,
            contentSample: contentDivs.length > 0 ? contentDivs[0].substring(0, 100) : ''
        });
    });
    return report;
    """
    res = driver.execute_script(js)
    print("Found articles in JS:", len(res))
    for r in res:
        print(f"\n================ ARTICLE {r['idx']} ================")
        print("Content sample:", r['contentSample'])
        print("SeeMores count:", len(r['seeMores']))
        for sm in r['seeMores']:
            print("  SEEMORE:", sm)
        print("Links count:", len(r['links']))
        for l in r['links']:
            print("  LINK:", l['href'][:90], "| TXT:", l['text'][:30], "| ARIA:", l['aria'][:30])
finally:
    driver.quit()
