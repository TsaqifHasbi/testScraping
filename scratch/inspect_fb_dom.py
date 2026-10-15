import os
import sys
import time
import urllib.parse
from bs4 import BeautifulSoup
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
    
    # Dump post elements info
    js_inspect = """
    let articles = document.querySelectorAll('div[role="article"]');
    let report = [];
    articles.forEach((art, idx) => {
        if (idx > 5) return;
        let links = Array.from(art.querySelectorAll('a[href]')).map(a => ({
            href: a.getAttribute('href'),
            text: a.innerText.trim(),
            aria: a.getAttribute('aria-label') || ''
        }));
        
        // Find See more elements
        let seeMores = [];
        art.querySelectorAll('*').forEach(el => {
            let t = (el.innerText || '').trim();
            if (/lihat selengkapnya|see more/i.test(t) && t.length < 30) {
                seeMores.push({
                    tag: el.tagName,
                    role: el.getAttribute('role'),
                    text: t,
                    className: el.className
                });
            }
        });
        
        report.push({
            idx: idx,
            links: links,
            seeMores: seeMores,
            outerHTMLSnippet: art.outerHTML.substring(0, 500)
        });
    });
    return report;
    """
    res = driver.execute_script(js_inspect)
    print("Found articles count:", len(res))
    for r in res:
        print(f"\n--- ARTICLE {r['idx']} ---")
        print("SeeMores found:", r['seeMores'])
        print("Links count:", len(r['links']))
        for l in r['links']:
            print("  LINK:", l['href'][:90], "| TXT:", l['text'][:30], "| ARIA:", l['aria'][:30])
finally:
    driver.quit()
