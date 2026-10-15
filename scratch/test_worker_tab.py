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

print("Starting driver...")
driver = uc.Chrome(options=options, version_main=154)
try:
    search_url = "https://www.facebook.com/search/posts/?q=Makan%20Bergizi%20Gratis"
    print("Navigating to search tab...")
    driver.get(search_url)
    time.sleep(4)
    
    search_tab = driver.current_window_handle
    
    # Create persistent worker tab
    print("Creating persistent worker tab...")
    driver.switch_to.new_window('tab')
    worker_tab = driver.current_window_handle
    
    # Test deep fetch on worker tab
    test_urls = [
        'https://www.facebook.com/photo/?fbid=2308481969997088&set=a.1667568807421744',
        'https://www.facebook.com/photo/?fbid=2312018026310149&set=a.1667568807421744'
    ]
    
    for u in test_urls:
        print(f"\nFetching on worker tab: {u[:60]}...")
        driver.get(u)
        time.sleep(3.5)
        
        # Expand see more if any on post viewer
        driver.execute_script("""
        document.querySelectorAll('div[role="button"], span[role="button"]').forEach(el => {
            let t = (el.innerText || '').trim().toLowerCase();
            if ((t === 'see more' || t === 'selengkapnya' || t === 'lihat selengkapnya' || t.endsWith('see more') || t.endsWith('selengkapnya')) && !el.closest('a')) {
                try { el.click(); } catch(e) {}
            }
        });
        """)
        time.sleep(1)
        
        caption = driver.execute_script("""
        let divs = Array.from(document.querySelectorAll('div[dir="auto"], span[dir="auto"]'))
            .map(d => (d.innerText || '').trim())
            .filter(t => t.length > 25 && !t.includes('Komentar') && !t.includes('Bagikan') && !t.includes('Suka') && !t.startsWith('http'));
        divs.sort((a, b) => b.length - a.length);
        return divs.length > 0 ? divs[0] : '';
        """)
        print(f"Result length: {len(caption)}")
        print(f"Snippet: {caption[:120]}...")
        
    # Return to search tab
    print("\nSwitching back to search tab...")
    driver.switch_to.window(search_tab)
    print(f"Search tab URL: {driver.current_url}")
    print("SUCCESS! Both tabs work without any invalid session error!")

finally:
    try:
        driver.quit()
    except Exception:
        pass
