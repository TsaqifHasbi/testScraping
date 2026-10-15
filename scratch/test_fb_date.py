import os
import sys
import time
import urllib.parse
import re
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
    
    js = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return [];
    
    return Array.from(feed.children).slice(0, 5).map((card, idx) => {
        let dates = [];
        // Check abbr, time, aria-labels with dates
        card.querySelectorAll('abbr, time, span, a').forEach(el => {
            let aria = el.getAttribute('aria-label') || '';
            let t = (el.innerText || '').trim();
            if (aria && /(menit|jam|hari|minggu|bulan|tahun|kemarin|yesterday|ago|hours?|mins?|days?|weeks?|months?|years?|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)|\d{4})/i.test(aria)) {
                dates.push({ type: 'aria', val: aria });
            }
            if (t && t.length < 35 && /(menit|jam|hari|minggu|kemarin|yesterday|ago|hours?|mins?|days?|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)|\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember))/i.test(t)) {
                dates.push({ type: 'text', val: t });
            }
        });
        return { idx: idx, dates: dates };
    });
    """
    res = driver.execute_script(js)
    for r in res:
        print(f"Card {r['idx']} dates:", r['dates'])
finally:
    driver.quit()
