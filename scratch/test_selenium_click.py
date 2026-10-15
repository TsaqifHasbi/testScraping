import os
import sys
import time
import urllib.parse
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
    
    # Find the first element with text "See more"
    els = driver.find_elements(By.XPATH, "//*[text()='See more' or text()='Lihat selengkapnya']")
    print(f"Found {len(els)} elements with exact text 'See more' / 'Lihat selengkapnya'")
    
    for idx, el in enumerate(els[:3]):
        print(f"\n--- Testing click on element {idx} ---")
        print("Tag:", el.tag_name, "| Displayed:", el.is_displayed(), "| Location:", el.location)
        
        # Get parent text before
        parent = el.find_element(By.XPATH, "./ancestor::div[contains(@class, 'html-div') or @dir='auto'][1]")
        print("Parent text BEFORE len:", len(parent.text))
        print("Parent snippet BEFORE:", parent.text[-60:])
        
        # Scroll to it and click using ActionChains
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.5)
        try:
            ActionChains(driver).move_to_element(el).click().perform()
            print("ActionChains click executed successfully!")
        except Exception as e:
            print("ActionChains error:", e)
            driver.execute_script("arguments[0].click();", el)
            
        time.sleep(1)
        print("Parent text AFTER len:", len(parent.text))
        print("Parent snippet AFTER:", parent.text[-60:])
finally:
    driver.quit()
