import os
import sys
import time
import urllib.parse
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
    
    # Get the timestamp link href
    js = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return null;
    let post = feed.children[0];
    let a = post.querySelector('a[target="_blank"][href^="?__cft__"]');
    return a ? a.getAttribute('href') : null;
    """
    href = driver.execute_script(js)
    print("Found href:", href[:60] if href else None)
    
    if href:
        full_url = "https://www.facebook.com/" + href
        print("Navigating to full_url...")
        driver.get(full_url)
        time.sleep(5)
        print("Resolved URL:", driver.current_url)
        print("Resolved Title:", driver.title)
finally:
    driver.quit()
