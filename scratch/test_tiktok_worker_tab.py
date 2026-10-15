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

print("Starting driver with 2 tabs...")
driver = uc.Chrome(options=options, version_main=154)
try:
    search_url = "https://www.tiktok.com/search/video?q=Makan%20Bergizi%20Gratis"
    driver.get(search_url)
    time.sleep(4)
    search_tab = driver.current_window_handle
    
    # Open worker tab
    driver.switch_to.new_window('tab')
    worker_tab = driver.current_window_handle
    
    # Test fetch
    video_url = "https://www.tiktok.com/@ampkpsu2/video/7695752035819457813"
    print(f"Fetching {video_url} on worker tab...")
    t0 = time.time()
    driver.get(video_url)
    time.sleep(3)
    
    desc = driver.execute_script("""
    let el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
    if (el) {
        try {
            let data = JSON.parse(el.innerText);
            let item = data?.['__DEFAULT_SCOPE__']?.['webapp.video-detail']?.['itemInfo']?.['itemStruct'] || {};
            return item.desc || '';
        } catch(e) {}
    }
    // Fallback DOM
    let textEls = document.querySelectorAll('div[data-e2e="browse-video-desc"], h1[data-e2e="browse-video-desc"], span[data-e2e="browse-video-desc"]');
    for (let el of textEls) {
        let t = (el.innerText || '').trim();
        if (t.length > 50) return t;
    }
    return '';
    """)
    dur = time.time() - t0
    print(f"Deep fetch took {dur:.2f}s! Result length: {len(desc)}")
    print(f"First 100 chars: {desc[:100]}...")
    print(f"Last 100 chars: ...{desc[-100:]}")
    
    # Switch back to search tab
    driver.switch_to.window(search_tab)
    print(f"Switched back to search tab: {driver.current_url}")
    print("SUCCESS!")

finally:
    try:
        driver.quit()
    except Exception:
        pass
