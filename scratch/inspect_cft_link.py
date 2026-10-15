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
from selenium.webdriver.common.action_chains import ActionChains

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
    
    # Let's inspect all links with ?__cft__ in the first post
    js = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    let post = feed.children[0];
    let links = Array.from(post.querySelectorAll('a[href]'));
    
    // Find the timestamp link (often below author)
    let cftLinks = links.filter(a => a.getAttribute('href').startsWith('?__cft__'));
    return cftLinks.map(a => {
        let attrs = {};
        for (let attr of a.attributes) {
            attrs[attr.name] = attr.value;
        }
        return {
            attrs: attrs,
            outerHTML: a.outerHTML.substring(0, 300),
            innerText: a.innerText
        };
    });
    """
    res = driver.execute_script(js)
    print("CFT links found:", len(res))
    for r in res:
        print("\nATTRS:", r['attrs'])
        print("HTML:", r['outerHTML'])
finally:
    driver.quit()
