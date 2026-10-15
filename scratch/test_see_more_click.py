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
    
    # Check text BEFORE click
    js_before = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return [];
    return Array.from(feed.children).map(c => {
        let txts = Array.from(c.querySelectorAll('div[dir="auto"], span[dir="auto"]'))
            .map(d => (d.innerText || '').trim())
            .filter(t => t.length > 20);
        return txts.length > 0 ? txts[0] : '';
    });
    """
    before_texts = driver.execute_script(js_before)
    print("Posts found:", len(before_texts))
    for i, t in enumerate(before_texts[:3]):
        print(f"Before [{i}] len={len(t)}: ends with '…' or '...'?", t.endswith('…') or t.endswith('...'))
        print("  Snippet:", t[-50:])
        
    # NOW CLICK ALL SEE MORE / LIHAT SELENGKAPNYA IN FEED!
    js_click = """
    let clickedCount = 0;
    // Find all buttons or clickable elements in document
    let allEls = document.querySelectorAll('div[role="button"], span[role="button"], div, span');
    allEls.forEach(el => {
        // Skip links or elements inside <a>
        if (el.tagName === 'A' || el.closest('a')) return;
        
        let t = (el.innerText || '').trim();
        // Match exact or ending with See more / Lihat selengkapnya
        if (/^(?:…|\\.\\.\\.)?\\s*(see more|lihat selengkapnya|selengkapnya)\\s*$/i.test(t) ||
            t === 'See more' || t === 'Lihat selengkapnya') {
            try {
                // Dispatch full pointer and mouse events
                ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(evt => {
                    el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
                });
                el.click();
                clickedCount++;
            } catch(e) {}
        }
    });
    return clickedCount;
    """
    clicked = driver.execute_script(js_click)
    print("\nClicked 'See more' elements:", clicked)
    time.sleep(2)
    
    # Check text AFTER click
    after_texts = driver.execute_script(js_before)
    for i, t in enumerate(after_texts[:3]):
        print(f"After [{i}] len={len(t)}: ends with '…' or '...'?", t.endswith('…') or t.endswith('...'))
        print("  Snippet:", t[-50:])
finally:
    driver.quit()
