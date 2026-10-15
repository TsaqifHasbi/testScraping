import undetected_chromedriver as uc
import os
import sys
import time

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

TIKTOK_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".tiktok_scraper_profile")
options = uc.ChromeOptions()
options.add_argument(f'--user-data-dir={TIKTOK_PROFILE_DIR}')
driver = uc.Chrome(options=options)
try:
    print("Testing existing TIKTOK_PROFILE_DIR on www.tiktok.com...")
    driver.get("https://www.tiktok.com/")
    time.sleep(5)
    print("Current URL:", driver.current_url)
    print("Title:", driver.title)
    text = driver.find_element("tag name", "body").text
    print("Body snippet (first 300 chars):", text[:300].replace('\n', ' '))
    if "403" in text or "Access to www.tiktok.com was denied" in text or "403" in driver.title:
        print("\n[CONFIRMED] Existing profile HAS 403 ERROR!")
    else:
        print("\n[RESULT] Profile loaded fine!")
finally:
    driver.quit()
