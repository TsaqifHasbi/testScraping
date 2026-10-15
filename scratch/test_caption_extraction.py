import os
import sys
import time
import urllib.parse
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

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
    
    # 1. Click all See more on feed with ActionChains
    see_mores = driver.find_elements(By.XPATH, "//*[text()='See more' or text()='Lihat selengkapnya']")
    print(f"Found {len(see_mores)} See more buttons. Clicking them...")
    for sm in see_mores:
        try:
            if sm.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sm)
                time.sleep(0.2)
                ActionChains(driver).move_to_element(sm).click().perform()
                time.sleep(0.3)
        except Exception:
            pass
            
    time.sleep(1)
    
    # 2. Extract content from feed items
    js_extract = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return [];
    
    let results = [];
    Array.from(feed.children).forEach((card, idx) => {
        // Find author
        let headerDiv = card.querySelector('h2, h3, h4');
        let author = headerDiv ? headerDiv.innerText.split('\\n')[0].trim() : '';
        
        // Find post content: div[dir="auto"] that is not header, not toolbar, not action button
        let textDivs = Array.from(card.querySelectorAll('div[dir="auto"], span[dir="auto"]'))
            .filter(d => !d.closest('a') && !d.closest('h2, h3, h4') && !d.closest('div[role="toolbar"]'))
            .map(d => (d.innerText || '').trim())
            .filter(t => t.length > 20 && 
                         !t.includes('\\u034f') &&
                         !/^(Komentar|Bagikan|Suka|Like|Comment|Share|Kirim|Send|Write a comment|Tulis komentar|Lihat komentar)/i.test(t));
                         
        // Sort by length to get main post caption
        textDivs.sort((a, b) => b.length - a.length);
        let content = textDivs.length > 0 ? textDivs[0] : '';
        
        results.push({
            idx: idx,
            author: author,
            contentLen: content.length,
            contentSnippet: content.substring(0, 80).replace(/\\n/g, ' '),
            contentEndsWithEllipsis: content.endsWith('…') || content.endsWith('...'),
            contentEnd: content.slice(-40).replace(/\\n/g, ' ')
        });
    });
    return results;
    """
    res = driver.execute_script(js_extract)
    print(f"\nExtracted {len(res)} cards:")
    for r in res[:6]:
        print(f"Card {r['idx']} | Author: {r['author'][:25]} | Len: {r['contentLen']} | Ends with ellipsis? {r['contentEndsWithEllipsis']}")
        print(f"  Snippet: {r['contentSnippet']}")
        print(f"  End    : {r['contentEnd']}")
finally:
    driver.quit()
