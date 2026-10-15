import os
import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

profile_dir = os.path.join(os.path.expanduser('~'), '.facebook_scraper_profile')
options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')
options.add_argument("--disable-notifications")
options.add_argument('--lang=id-ID,id,en-US,en')
options.add_argument(f'--user-data-dir={profile_dir}')

print("Starting Chrome...")
driver = uc.Chrome(options=options, version_main=154)
try:
    url = "https://www.facebook.com/search/posts/?q=Makan%20Bergizi%20Gratis"
    print(f"Navigating to {url}...")
    driver.get(url)
    time.sleep(6)

    # Inspect articles and see-more elements
    res = driver.execute_script("""
    let articles = document.querySelectorAll('div[role="article"]');
    let report = [];
    for (let i = 0; i < Math.min(articles.length, 10); i++) {
        let art = articles[i];
        let allEls = art.querySelectorAll('*');
        let seeMoreMatches = [];
        for (let el of allEls) {
            let txt = (el.innerText || '').trim();
            if (/selengkapnya|see more|lainnya/i.test(txt) && txt.length < 30) {
                seeMoreMatches.push({
                    tag: el.tagName,
                    role: el.getAttribute('role'),
                    text: txt,
                    classes: el.className,
                    isLink: !!(el.tagName === 'A' || el.closest('a')),
                    offsetParent: !!el.offsetParent
                });
            }
        }
        
        let contentDivs = art.querySelectorAll('div[dir="auto"]');
        let texts = Array.from(contentDivs).map(c => c.innerText.trim()).filter(t => t.length > 15);
        report.push({
            index: i,
            seeMoreCount: seeMoreMatches.length,
            seeMoreSample: seeMoreMatches.slice(0, 5),
            textSnippets: texts.map(t => t.substring(0, 80) + '... (len: ' + t.length + ')')
        });
    }
    return report;
    """)

    print("\n--- REPORT ---")
    import json
    print(json.dumps(res, indent=2))

finally:
    driver.quit()
