with open('c:/Users/Asus/OneDrive/Documents/Project_Streamlit/cobaAPI/colab_cells/cell_04_twitter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '    # Kumpulkan URL tweet dari halaman search' in line:
        skip = True
        
        # INSERT NEW LOGIC
        new_logic = '''    # Kumpulkan Data tweet dari halaman search secara LANGSUNG (Single-Phase)
    all_tweet_data = {} # dictionary url -> data
    last_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
    no_new_count = 0
    max_no_new = 8
    
    collect_data_js = """
    const results = [];
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    for (const article of articles) {
        try {
            let tweetUrl = '';
            const links = article.querySelectorAll('a[href*="/status/"]');
            for (const link of links) {
                if (link.href.includes('/status/') && !link.href.includes('/photo/') && !link.href.includes('/video/') && !link.href.includes('/analytics')) {
                    tweetUrl = link.href.split('?')[0];
                    break;
                }
            }
            if (!tweetUrl) continue;

            let dateStr = '';
            const timeEl = article.querySelector('time');
            if (timeEl) dateStr = timeEl.getAttribute('datetime') || '';

            let text = '';
            const textDiv = article.querySelector('div[data-testid="tweetText"]');
            if (textDiv) text = textDiv.innerText;

            let handle = '';
            const userLinks = article.querySelectorAll('a[role="link"]');
            for (const ul of userLinks) {
                const textContent = ul.innerText;
                if (textContent.includes('@')) {
                    const match = textContent.match(/@[\\w_]+/);
                    if (match) {
                        handle = match[0];
                        break;
                    }
                }
            }

            let likes=0, views=0, retweets=0, replies=0;
            const groups = article.querySelectorAll('[role="group"]');
            if (groups.length > 0) {
                const btns = groups[0].querySelectorAll('[role="button"], a');
                for (const btn of btns) {
                    const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const testId = (btn.getAttribute('data-testid') || '').toLowerCase();
                    let valStr = btn.innerText.trim();
                    
                    let val = 0;
                    if (valStr) {
                        valStr = valStr.replace(/,/g, '');
                        if (valStr.match(/K/i)) val = parseFloat(valStr) * 1000;
                        else if (valStr.match(/M/i)) val = parseFloat(valStr) * 1000000;
                        else val = parseInt(valStr) || 0;
                    }

                    if (testId === 'reply' || aria.includes('balas') || aria.includes('reply')) replies = val;
                    else if (testId === 'retweet' || aria.includes('repost') || aria.includes('retweet')) retweets = val;
                    else if (testId === 'like' || aria.includes('suka') || aria.includes('like')) likes = val;
                    else if (aria.includes('tayangan') || aria.includes('view') || testId.includes('view')) views = val;
                }
            }

            results.push({
                url: tweetUrl,
                date: dateStr,
                text: text,
                username: handle,
                likes: likes,
                views: views,
                retweets: retweets,
                replies: replies
            });
        } catch(e) {}
    }
    return results;
    """

    while len(all_tweet_data) < max_results:
        try:
            extracted_data = TWITTER_DRIVER.execute_script(collect_data_js)
            count_before = len(all_tweet_data)

            for item in (extracted_data or []):
                tweet_url = item.get('url', '')
                if not tweet_url or tweet_url in all_tweet_data or tweet_url in _SEEN_URLS:
                    continue
                all_tweet_data[tweet_url] = item

            new_count = len(all_tweet_data) - count_before
            if new_count > 0:
                print(f"      [Scroll] {len(all_tweet_data)} Data terkumpul (+{new_count} baru)")

            if new_count == 0:
                clicked_retry = TWITTER_DRIVER.execute_script("""
                    let btns = document.querySelectorAll('div[data-testid="primaryColumn"] button');
                    for (let btn of btns) {
                        let txt = btn.innerText.toLowerCase();
                        if (txt.includes('retry') || txt.includes('coba lagi')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if clicked_retry:
                    print("      [INFO] Jaringan Twitter melambat. Menekan tombol 'Retry / Coba lagi'...")
                    time.sleep(5)
                    continue

                no_new_count += 1
                if no_new_count >= max_no_new:
                    if len(all_tweet_data) < max_results and "&f=live" not in url and max_results >= 1000:
                        print(f"    [INFO] Tab 'Top' habis ({len(all_tweet_data)} data). Beralih otomatis ke tab 'Latest' untuk melengkapi {max_results}...")
                        url = url + "&f=live"
                        TWITTER_DRIVER.get(url)
                        no_new_count = 0
                        time.sleep(5)
                        continue
                    else:
                        print(f"    [INFO] Mentok maksimal! {max_no_new}x scroll tanpa data baru. Berhenti.")
                        break
            else:
                no_new_count = 0

            if len(all_tweet_data) >= max_results:
                break

            TWITTER_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.0, 4.0))

            body_text = (TWITTER_DRIVER.execute_script("return document.body.innerText") or "").lower()
            if "something went wrong" in body_text or "ada yang salah" in body_text or "try reloading" in body_text or "kesalahan teknis" in body_text or "muat ulang" in body_text:
                print("\\n    [!] ERROR DI TENGAH SCROLL: Twitter memblokir pencarian.")
                print("    [INFO] Memaksa logout...")
                TWITTER_DRIVER.delete_all_cookies()
                TWITTER_DRIVER.get("https://x.com/login")
                time.sleep(3)
                
                print("\\n" + "=" * 60)
                print("🚨 SESI TWITTER KEDALUWARSA / LIMIT DI TENGAH JALAN 🚨")
                print("1. Silakan LOGIN ULANG (pakai AKUN TWITTER LAIN jika limit).")
                print("2. Jika pencarian manual berhasil, kembali ke sini dan tekan ENTER.")
                print("=" * 60 + "\\n")
                
                input("👉 TEKAN ENTER JIKA SUDAH LOGIN ULANG & AMAN... ")
                
                print("    [INFO] Melanjutkan pencarian (scroll ulang dari atas)...")
                TWITTER_DRIVER.get(url)
                time.sleep(5)
                continue

            new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(2)
                new_height = TWITTER_DRIVER.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_new_count += 1
            last_height = new_height

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"    [WARN] Error saat scroll: {e}")
            break

    print(f"    [INFO] Selesai. Total {len(all_tweet_data)} data tweet berhasil diekstrak.")
    
    # Format hasil akhir
    final_data = []
    for item in all_tweet_data.values():
        date_str = item['date']
        
        final_data.append({
            'platform': 'Twitter',
            'keyword': keyword,
            'url': item['url'],
            'handle': item['username'],
            'content': item['text'],
            'created_at': _to_wib(date_str),
            'likes': item['likes'],
            'comments': item['replies'],
            'reposts': item['retweets'],
            'views': item['views'],
            'scraped_at': datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S') + ' WIB',
        })
        _SEEN_URLS.add(item['url'])

    return final_data
'''
        new_lines.append(new_logic)
        
    if skip and '    return results' in line:
        skip = False
        continue
        
    if not skip:
        new_lines.append(line)

with open('c:/Users/Asus/OneDrive/Documents/Project_Streamlit/cobaAPI/colab_cells/cell_04_twitter.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
