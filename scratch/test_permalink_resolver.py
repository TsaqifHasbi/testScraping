import os
import sys
import time
import urllib.parse
import re
import undetected_chromedriver as uc
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
    
    js_extract_posts = """
    let feed = document.querySelector('div[role="feed"]');
    if (!feed) return [];
    
    let posts = [];
    Array.from(feed.children).forEach((card, idx) => {
        // Collect all links in this card
        let links = Array.from(card.querySelectorAll('a[href]')).map(a => a.getAttribute('href'));
        let text = (card.innerText || '').trim();
        
        // Filter out stories, share dialogs, hashtags
        let cleanLinks = links.filter(h => {
            if (!h) return false;
            if (h.includes('/stories/')) return false;
            if (h.includes('sharer.php') || h.includes('dialog/share')) return false;
            if (h.includes('hashtag/')) return false;
            if (h.startsWith('#')) return false;
            return true;
        });
        
        posts.push({
            idx: idx,
            textSnippet: text.substring(0, 120).replace(/\\n/g, ' '),
            cleanLinks: cleanLinks
        });
    });
    return posts;
    """
    posts = driver.execute_script(js_extract_posts)
    print(f"Extracted {len(posts)} posts from feed.")
    
    def resolve_post_permalink(links):
        """
        Aturan resolusi URL Post Permanen Facebook:
        1. Jangan pernah ambil /stories/
        2. Jangan pernah ambil root group /groups/<id>/ tanpa posts/permalink
        3. Prioritas:
           - https://facebook.com/groups/<group_id>/posts/<post_id>/
           - https://facebook.com/groups/<group_id>/permalink/<post_id>/
           - https://facebook.com/<user_id>/posts/<post_id>/
           - https://facebook.com/permalink.php?story_fbid=...
           - https://facebook.com/reel/<id> atau /watch/?v=<id> atau /videos/<id>
           - Konversi photo dengan set=gm.<post_id>&idorvanity=<group_id> -> /groups/<group_id>/posts/<post_id>/
           - Konversi photo dengan set=pcb.<post_id> -> /posts/<post_id>/
           - Fallback photo: https://facebook.com/photo/?fbid=...
        """
        # A. Cek apakah ada direct post permalink di group
        for l in links:
            if re.search(r'/groups/[^/?]+/posts/\d+', l) or re.search(r'/groups/[^/?]+/permalink/\d+', l):
                clean = l.split('?')[0] if '?' in l else l
                return "https://www.facebook.com" + clean if clean.startswith('/') else clean
                
        # B. Cek apakah ada user direct post permalink (/posts/ atau /permalink.php)
        for l in links:
            if '/posts/' in l and not l.startswith('/groups/'):
                clean = l.split('?')[0] if '?' in l else l
                return "https://www.facebook.com" + clean if clean.startswith('/') else clean
            if 'permalink.php' in l and 'story_fbid=' in l:
                clean = l.split('&__cft__')[0].split('?__cft__')[0]
                return "https://www.facebook.com" + clean if clean.startswith('/') else clean
                
        # C. Cek video / reel
        for l in links:
            if '/reel/' in l or '/videos/' in l or '/watch/' in l:
                clean = l.split('?')[0] if '?' in l else l
                return "https://www.facebook.com" + clean if clean.startswith('/') else clean
                
        # D. Rekonstruksi dari photo jika ada parameter set=gm (Group post) atau set=pcb (Profile post)
        for l in links:
            if '/photo' in l or 'fbid=' in l:
                # Cek set=gm.<post_id>&idorvanity=<group_id>
                m_gm = re.search(r'set=gm\.(\d+)', l)
                m_grp = re.search(r'idorvanity=(\d+)', l)
                if m_gm and m_grp:
                    return f"https://www.facebook.com/groups/{m_grp.group(1)}/posts/{m_gm.group(1)}/"
                elif m_gm:
                    # Cari group ID dari link lain di card yang sama
                    for other in links:
                        m_other_grp = re.search(r'/groups/(\d+)', other)
                        if m_other_grp:
                            return f"https://www.facebook.com/groups/{m_other_grp.group(1)}/posts/{m_gm.group(1)}/"
                            
                # Cek set=pcb.<post_id>
                m_pcb = re.search(r'set=pcb\.(\d+)', l)
                if m_pcb:
                    # Cari user/author ID dari link lain di card yang sama
                    author_id = None
                    for other in links:
                        m_u = re.search(r'profile\.php\?id=(\d+)', other)
                        if m_u:
                            author_id = m_u.group(1)
                            break
                        m_u2 = re.search(r'facebook\.com/([^/?]+)', other)
                        if m_u2 and m_u2.group(1) not in ['photo', 'groups', 'pages', 'watch', 'reel']:
                            author_id = m_u2.group(1)
                            break
                    if author_id:
                        return f"https://www.facebook.com/{author_id}/posts/{m_pcb.group(1)}/"
                    else:
                        # Fallback clean photo url
                        fbid = re.search(r'fbid=(\d+)', l)
                        if fbid:
                            return f"https://www.facebook.com/photo/?fbid={fbid.group(1)}&set=pcb.{m_pcb.group(1)}"
                            
                # Fallback clean photo URL
                fbid = re.search(r'fbid=(\d+)', l)
                if fbid:
                    return f"https://www.facebook.com/photo/?fbid={fbid.group(1)}"

        # E. JANGAN PERNAH return link grup homepage atau profile homepage!
        return None

    for p in posts[:6]:
        resolved = resolve_post_permalink(p['cleanLinks'])
        print(f"\n--- Post {p['idx']} ---")
        print("Text:", p['textSnippet'][:80])
        print("Resolved Permalink:", resolved)
        print("Raw links:")
        for l in p['cleanLinks']:
            print("  ", l[:85])
finally:
    driver.quit()
