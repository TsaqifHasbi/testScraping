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
    url = 'https://www.facebook.com/photo/?fbid=2308481969997088&set=a.1667568807421744'
    driver.get(url)
    time.sleep(4)
    
    # Try expanding See More on the photo viewer
    expand_res = driver.execute_script("""
    let seeMores = Array.from(document.querySelectorAll('div[role="button"], span[role="button"], span, div'))
        .filter(el => {
            let txt = (el.innerText || '').trim().toLowerCase();
            return (txt === 'see more' || txt === 'lihat selengkapnya' || txt === 'selengkapnya' || txt.endsWith('see more') || txt.endsWith('selengkapnya')) && !el.closest('a') && el.tagName !== 'A';
        });
    let clicked = 0;
    seeMores.forEach(el => {
        try {
            ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(evt => {
                el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            });
            el.click();
            clicked++;
        } catch(e) {}
    });
    return { found: seeMores.length, clicked: clicked };
    """)
    print("Expansion result:", expand_res)
    time.sleep(2)

    script = """
    let divs = document.querySelectorAll('div[dir="auto"], span[dir="auto"]');
    let texts = [];
    for (let d of divs) {
        let t = (d.innerText || '').trim();
        if (t.length > 30 && !t.includes('Komentar') && !t.includes('Bagikan')) {
            texts.push(t);
        }
    }
    return texts;
    """
    txt = driver.execute_script(script)
    for t in txt[:3]:
        print("--- LEN", len(t), "---")
        print(t)
finally:
    try:
        driver.quit()
    except Exception:
        pass
