import os
import sys
import time
import undetected_chromedriver as uc

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

profile_dir = os.path.join(os.path.expanduser('~'), '.tiktok_scraper_profile')
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument(f'--user-data-dir={profile_dir}')

print("Launching Chrome for TikTok video test...")
driver = uc.Chrome(options=options, version_main=154)
try:
    url = "https://www.tiktok.com/@ampkpsu2/video/7695752035819457813"
    print(f"Opening video {url}...")
    driver.get(url)
    time.sleep(5)
    
    # 1. Check DOM caption
    dom_text = driver.execute_script("""
    // Cari elemen caption video di TikTok
    let selectors = [
        'div[data-e2e="browse-video-desc"]',
        'span[data-e2e="browse-video-desc"]',
        'h1[data-e2e="browse-video-desc"]',
        'div[class*="DivTextContainer"]',
        'span[class*="SpanText"]',
        'h1'
    ];
    let found = [];
    for (let s of selectors) {
        document.querySelectorAll(s).forEach(el => {
            let t = (el.innerText || '').trim();
            if (t.length > 30) found.push({ selector: s, text: t, len: t.length });
        });
    }
    return found;
    """)
    print("\n--- DOM CAPTIONS FOUND ---")
    for d in dom_text[:3]:
        print(f"Selector: {d['selector']} | Len: {d['len']}")
        print(f"Snippet: {d['text'][:150]}...")
        print(f"End: ...{d['text'][-60:]}")
        
    # 2. Check JSON data in page
    json_text = driver.execute_script("""
    let el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
    if (el) {
        try {
            let data = JSON.parse(el.innerText);
            let defaultScope = data['__DEFAULT_SCOPE__'] || {};
            let detail = defaultScope['webapp.video-detail'] || {};
            let item = (detail.itemInfo && detail.itemInfo.itemStruct) || {};
            return {
                desc: item.desc || '',
                descLen: (item.desc || '').length
            };
        } catch(e) {
            return { error: String(e) };
        }
    }
    return { noElement: true };
    """)
    print("\n--- JSON REHYDRATION DATA ---")
    print("JSON result:", json_text)

finally:
    try:
        driver.quit()
    except Exception:
        pass
