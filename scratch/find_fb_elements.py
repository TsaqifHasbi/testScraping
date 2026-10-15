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
    time.sleep(6)
    
    # Let's inspect what elements have role, or what containers exist
    js = """
    let roles = {};
    document.querySelectorAll('*[role]').forEach(el => {
        let r = el.getAttribute('role');
        roles[r] = (roles[r] || 0) + 1;
    });
    
    // Find all links containing /posts/ or /groups/ or photo or similar
    let postLinks = Array.from(document.querySelectorAll('a[href]'))
        .map(a => a.getAttribute('href'))
        .filter(h => h && (h.includes('/posts/') || h.includes('/permalink/') || h.includes('fbid=') || h.includes('/photo/')));
        
    return {
        roles: roles,
        postLinksCount: postLinks.length,
        sampleLinks: postLinks.slice(0, 10),
        mainPresent: !!document.querySelector('div[role="main"]'),
        feedPresent: !!document.querySelector('div[role="feed"]')
    };
    """
    res = driver.execute_script(js)
    print("Roles found:", res['roles'])
    print("Post links found count:", res['postLinksCount'])
    print("Main present:", res['mainPresent'])
    print("Feed present:", res['feedPresent'])
    print("Sample links:")
    for l in res['sampleLinks']:
        print(" ", l[:100])
finally:
    driver.quit()
