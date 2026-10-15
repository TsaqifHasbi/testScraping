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
    print("Opening search page...")
    driver.get(search_url)
    time.sleep(5)
    main_handle = driver.current_window_handle
    
    test_post_url = 'https://www.facebook.com/photo/?fbid=2308481969997088&set=a.1667568807421744'
    print(f"Opening post in new tab: {test_post_url}...")
    t0 = time.time()
    driver.execute_script(f"window.open('{test_post_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    
    full_text = driver.execute_script("""
        let divs = document.querySelectorAll('div[dir="auto"], span[dir="auto"]');
        let texts = [];
        for (let d of divs) {
            let t = (d.innerText || '').trim();
            if (t.length > 30 && !t.includes('Komentar') && !t.includes('Bagikan')) {
                texts.push(t);
            }
        }
        // Ambil teks terpanjang
        texts.sort((a, b) => b.length - a.length);
        return texts.length > 0 ? texts[0] : '';
    """)
    driver.close()
    driver.switch_to.window(main_handle)
    dur = time.time() - t0
    
    print(f"Deep fetch succeeded in {dur:.2f}s!")
    print(f"Full text length: {len(full_text)}")
    print(f"Full text snippet: {full_text[:200]}...")
    print(f"Active URL after return: {driver.current_url}")
finally:
    try:
        driver.quit()
    except Exception:
        pass
