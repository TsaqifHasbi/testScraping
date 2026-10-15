import undetected_chromedriver as uc
import os
import time

# 1. Test clean profile
options = uc.ChromeOptions()
options.add_argument('--lang=id-ID,id,en-US,en')
driver = uc.Chrome(options=options)
try:
    print("Testing clean profile on www.tiktok.com...")
    driver.get("https://www.tiktok.com/")
    time.sleep(5)
    print("Current URL:", driver.current_url)
    print("Title:", driver.title)
    text = driver.find_element("tag name", "body").text
    print("Body snippet:", text[:200].replace('\n', ' '))
    if "403" in text or "Access to www.tiktok.com was denied" in text:
        print("[RESULT] Clean profile STILL GETS 403! (IP or Cloudflare/Akamai block)")
    else:
        print("[RESULT] Clean profile SUCCEEDS! (Issue was the corrupted scraper profile)")
finally:
    driver.quit()
