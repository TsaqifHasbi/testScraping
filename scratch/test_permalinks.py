import os
import sys
import time
import undetected_chromedriver as uc

FB_PROFILE_DIR = os.path.join(os.path.expanduser('~'), '.facebook_scraper_profile')

options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')
options.add_argument("--disable-notifications")
options.add_argument('--lang=id-ID,id,en-US,en')
options.add_argument(f'--user-data-dir={FB_PROFILE_DIR}')

driver = uc.Chrome(options=options)
try:
    test_urls = [
        # Group post
        "https://www.facebook.com/groups/648936018837359/posts/2789970578067215/",
        "https://www.facebook.com/groups/648936018837359/permalink/2789970578067215/",
        # User post from pcb
        "https://www.facebook.com/61587331624837/posts/122136472455244387/",
        "https://www.facebook.com/permalink.php?story_fbid=122136472455244387&id=61587331624837",
        # Photo post
        "https://www.facebook.com/photo/?fbid=122136472431244387&set=pcb.122136472455244387"
    ]
    
    for u in test_urls:
        driver.get(u)
        time.sleep(4)
        print("Requested:", u)
        print("Result   :", driver.current_url)
        print("Title    :", driver.title)
        print("Body len :", len(driver.find_element("tag name", "body").text))
        print("---")
finally:
    driver.quit()
