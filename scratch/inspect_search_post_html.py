import os
import sys
import time
import undetected_chromedriver as uc

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

profile_dir = os.path.join(os.path.expanduser('~'), '.facebook_scraper_profile')
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument(f'--user-data-dir={profile_dir}')

driver = uc.Chrome(options=options, version_main=154)
try:
    search_url = "https://www.facebook.com/search/posts/?q=Makan%20Bergizi%20Gratis"
    print("Navigating to search...")
    driver.get(search_url)
    time.sleep(6)
    
    # Scroll 2 times to load posts
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    res = driver.execute_script("""
    let articles = document.querySelectorAll('div[role="article"]');
    let out = [];
    for (let art of articles) {
        let text = art.innerText || '';
        // Look for any post that has ... or ellipsis
        if (text.includes('…') || text.includes('...')) {
            // Find all buttons or spans in this article
            let btns = Array.from(art.querySelectorAll('*'))
                .filter(el => {
                    let t = (el.innerText || '').trim();
                    return t.length > 0 && t.length < 35 && /selengkapnya|see more|more|lainnya/i.test(t);
                })
                .map(el => ({
                    tag: el.tagName,
                    role: el.getAttribute('role'),
                    text: el.innerText.trim(),
                    className: el.className,
                    isLink: !!(el.tagName === 'A' || el.closest('a'))
                }));
            out.push({
                snippet: text.substring(0, 150),
                totalLen: text.length,
                potentialButtons: btns
            });
            if (out.length >= 5) break;
        }
    }
    return out;
    """)

    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))

finally:
    try:
        driver.quit()
    except Exception:
        pass
