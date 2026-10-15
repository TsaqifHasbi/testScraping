import os
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
    time.sleep(6)
    
    print("URL:", driver.current_url)
    print("Title:", driver.title)
    text = driver.find_element("tag name", "body").text
    print("Body text snippet (first 600 chars):")
    print(text[:600])
    
    # Check elements with role="feed" or role="main" or role="article"
    js = """
    return {
        roles: Array.from(document.querySelectorAll('[role]')).map(e => e.getAttribute('role')),
        divsWithText: Array.from(document.querySelectorAll('div')).filter(d => d.innerText && d.innerText.includes('Makan')).length,
        linksCount: document.querySelectorAll('a[href]').length
    };
    """
    stats = driver.execute_script(js)
    print("DOM Stats:", stats['linksCount'], "links,", stats['divsWithText'], "divs with Makan")
    print("Distinct roles:", set(stats['roles']))
finally:
    driver.quit()
