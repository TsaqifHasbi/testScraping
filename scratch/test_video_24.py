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

driver = uc.Chrome(options=options, version_main=154)
try:
    url = "https://www.tiktok.com/@nalarmerdeka/video/7695812430752009492"
    driver.get(url)
    time.sleep(5)
    
    desc = driver.execute_script("""
    let el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
    if (el) {
        try {
            let data = JSON.parse(el.innerText);
            let item = data?.['__DEFAULT_SCOPE__']?.['webapp.video-detail']?.['itemInfo']?.['itemStruct'] || {};
            return {
                desc: item.desc || '',
                stats: item.stats || {}
            };
        } catch(e) {}
    }
    return {};
    """)
    print("Video 24 actual data:")
    print("Desc length:", len(desc.get('desc', '')))
    print("Full Desc:\n", desc.get('desc', ''))
    print("Stats:", desc.get('stats', {}))
finally:
    driver.quit()
