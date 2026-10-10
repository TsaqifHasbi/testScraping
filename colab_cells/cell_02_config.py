# ============================================================
# CELL 2: KONFIGURASI KREDENSIAL & TOPIK PENELITIAN
# Isi semua credential di bawah ini sebelum menjalankan scraping
# ============================================================

import os
# pyrefly: ignore [missing-import]
import nest_asyncio
nest_asyncio.apply()

# ================================================================
# DIREKTORI OUTPUT (Path Lokal Windows)
# ================================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ScrapeData')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================================================================
# YOUTUBE — YouTube Data API v3 Key
# Cara: Dapatkan API Key gratis di Google Cloud Console
# ================================================================
YOUTUBE_API_KEY = "AIzaSyBrHrRXtaKDwAxlAY8gudXjnEb9F6jaPvw"

# ================================================================
# TWITTER/X — Cookie dari browser
# Cara: Login Twitter di browser > F12 > Application > Cookies > x.com
#        Cari cookie bernama "auth_token" dan "ct0", copy nilainya
# ================================================================
TWITTER_COOKIES = {
    "auth_token": "687912004832a6234b5abcd93fad043ea267297d",
    "ct0": "1511710ab6133140b5e53033eb304ac563dda9643151557a41b65f4dee289a7b2fc9ec94e2da88946013d2bd7057caf05b49529a737d9075145d13b8c8b780473ffae48c74767babde6460cf7a8dc091",
}

# ================================================================
# TIKTOK — Cookie dari browser
# Cara: Login TikTok di browser > F12 > Application > Cookies > tiktok.com
#        Copy semua cookie sebagai string "key1=val1; key2=val2; ..."
# ================================================================
TIKTOK_COOKIE = """delay_guest_mode_vid=5; g_state={"i_l":0,"i_ll":1782032495741,"i_b":"dBXb7unjIx9Yrqv6ZRXqzjduVh77FIgS/z1kLpU5RJU","i_e":{"enable_itp_optimization":24},"i_et":1782032495741}; last_login_method=google; _ttp=3Fkw4wHiesRWMah2CKvIPiWWeLH; passport_csrf_token=ad93fec592e3e1a3988700f04a58adfe; passport_csrf_token_default=ad93fec592e3e1a3988700f04a58adfe; myCookie=rap; s_v_web_id=verify_mudom0wp_e0oSJ2sB_XfHU_4S1S_9UoK_f6SGhQdpFwko; tiktok_webapp_theme_source=auto; tiktok_webapp_theme=dark; tt_ticket_guard_has_set_public_key=1; passport_fe_beating_status=true; waforiginalreid=https://www.tiktok.com/; waforigin_id=44; _waftokenid=eyJ2Ijp7ImEiOiIvRWswQ1JLdytYU092T3hEbnFOQktwQWhkdTFOMVRvSkFiYXVrVW5UVExZPSIsImIiOjE3OTA2MTE1MDUsImMiOiJYb3BrY3llWkU0RHM2aWVycm44dGdhNi96TG9iL245aG1mamJoc2orbENJPSJ9LCJzIjoiU0ZuZHVYM1pUeEJEUWlkVkY5eW5XU0F3ZjNOQVozYXlVNjZzekQxbCtGYz0ifQ; msToken=8Dwa7OAKeUeAG3S7OZxhHAvdTUqJWMt7A-rRWdcOTk5_5VrYulMwcV7WcQNIvUVHMiZPv5agmLIhRxXoFn_gB4Ru8jtRZqTvk8j9mWvNqeXBOIGIxs_3npUINIXRK-R26KvMwxyGmcIEfU4mGeUdGqMA7hrlAoo4dbcANmVrPzI=; msToken=jCECxiDQ7zrlTUx9ISqhQIA2MgeqgD41TIW-EDuTU1zYavfXxUhCdEzkKSo8JHH8HW8twrAw2KAEMLPMbhB4YtE1yoPc5CJ8WmgLijMCishl2BkWvFwgYkz5gBwM5kUE3wf047IPbnSDzCk2EXa5_VPlaK7aKtv2EeF8Qmzktw==; perf_feed_cache={%22expireTimestamp%22:1791216000000%2C%22itemIds%22:[%227679111944200080658%22%2C%227685070548908412181%22%2C%227690608911828667670%22]}"""

# ================================================================
# INSTAGRAM — Akun dummy & Cookie Playwright
# ================================================================
IG_USERNAME = "scrapetsf_"
IG_PASSWORD = "Aghnasyarief3"
IG_COOKIE = "csrftoken=DcZZYVGNmquGu7LSwg0xKMkn9xFwdxkC; datr=Q880aqZUWs4FdxgCLTE5HpfM; dpr=1.25; ds_user_id=14889043079; ig_did=C6CF683D-04A5-45B4-A343-847BCB126C5F; ig_nrcb=1; mid=ajTPQwALAAG_xKDu3DzHJhAx6ox7; ps_l=1; ps_n=1; rur=PRN%2C17841414972371130%2C1791820760%3A01ff6e107617788e03a2e212e684571f27633f3da32e84fb98e44eaee9c172ab247e1186; sessionid=14889043079%3AaTerSZeSX4BVU2%3A25%3AAYmNbdBo3qyH3uQLWC16nFdgqDt_c_ZUdf2p7FLdow; wd=982x742"

# ================================================================
# FACEBOOK — Cookie dari browser
# Cara: Login Facebook di browser > F12 > Application > Cookies > facebook.com
#        Copy semua cookie sebagai string "key1=val1; key2=val2; ..."
# ================================================================
FB_COOKIE = """locale=en_GB; dpr=1.25; c_user=61594469380108; xs=2:dwOR1nXMyApMJA:2:1790611279:-1:-1::AcwhG5CIuo5Mv_M3Es4jijJNllCV7QekzKfD6BgS2w; datr=kbk3arcnLLX4WpPK39N0LkG1; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1790611287010%2C%22v%22%3A1%7D; wd=982x742"""

# ================================================================
# TOPIK PENELITIAN — 3 Program Pemerintah
# Setiap topik punya banyak variasi keyword untuk memperbanyak data
# ================================================================
TOPICS = {
    "MBG": [
        # Keyword utama
        "Makan Bergizi Gratis",
        "MBG",
        "makan bergizi gratis 2025",
        "makan bergizi gratis 2026",
        "makan bergizi gratis sekolah",
        "program makan bergizi gratis",
        "makan bergizi gratis pesantren",
        "makan bergizi gratis ibu hamil",
        "makanan bergizi gratis siswa",
        "program MBG",
        "MBG prabowo",
        "MBG 2025",
        "MBG 2026",
        "MBG ibu hamil",
        # Keyword viral/kontroversi
        "BGN makan bergizi gratis",
        "makan bergizi gratis korupsi",
        # "korupsi makan bergizi gratis",
        "Makan Bergizi Gratis BGN",
        "program makan bergizi gratis BGN",
        "makan bergizi gratis kontroversi",
        "SPPG makan bergizi gratis",
        "kasus makan bergizi gratis",
        # "makan bergizi gratis kasus",
        "kasus MBG",
        # "MBG kasus",
        "keracunan MBG",
        # "MBG keracunan",
        # "MBG korupsi",
        "korupsi MBG",
        "MBG BGN",
        "MBG viral",
        "MBG SPPG",
        # Keyword lembaga & tokoh
        # "MBG Dadan Hindayana",
        "Satuan Pelayanan Pemenuhan Gizi",
        # "catering MBG",
        "menu MBG",
        "anggaran MBG",
        "MBG stunting",
        # Keyword opini publik
        "MBG gagal",
        "MBG berhasil",
        "MBG positif",
        "MBG negatif",
        "MBG🔥",
        "MBG👍",
        "MBG👎",
        "MBG💩",
        "MBG🚀",
        "MBG✨",
        "MBG🎉",
        "MBG💯",
        "Makan Bergizi Gratis🔥",
        "Makan Bergizi Gratis👍",
        "Makan Bergizi Gratis👎",
        "Makan Bergizi Gratis💩",
        "Makan Bergizi Gratis🚀",
        "Makan Bergizi Gratis✨",
        "Makan Bergizi Gratis🎉",
        "Makan Bergizi Gratis💯",
        "program makan bergizi gratis gagal",
        "program makan bergizi gratis berhasil",
        "MBG kritik",
        "kualitas makanan MBG",
        "MBG sekolah dasar",
        "MBG SMA",
    ],
    "KDMP": [
        # Keyword utama
        "KDMP",
        "Koperasi Desa Merah Putih",
        "Program Koperasi Desa Merah Putih",
        "Koperasi Desa Merah Putih 2025",
        "Koperasi Desa Merah Putih 2026",
        "koperasi desa",
        # "koperasi merah putih",
        "KDMP 2025",
        "KDMP 2026",
        "koperasi desa merah putih prabowo",
        "program KDMP",
        "koperasi desa merah putih baru",
        # "KDMP koperasi",
        "dana desa koperasi",
        "koperasi UMKM desa",
        "pemberdayaan desa koperasi",
        # Keyword tambahan
        "koperasi desa merah putih korupsi",
        # "korupsi koperasi desa merah putih",
        "KDMP korupsi",
        # "korupsi KDMP",
        # "KDMP BUMDes",
        # "koperasi rakyat desa",
        "KDMP kontroversi",
        # "Koperasi Desa Merah Putih Kasus",
        "Kasus Koperasi Desa Merah Putih",
        "kasus KDMP",
        # "KDMP Kasus",
        # Keyword lembaga & tokoh
        "koperasi desa merah putih modern",
        "KDMP dana desa",
        # Keyword opini publik
        "KDMP gagal",
        "KDMP berhasil",
        "KDMP positif",
        "KDMP negatif",
        "KDMP🔥",
        "KDMP👍",
        "KDMP👎",
        "KDMP💩",
        "KDMP🚀",
        "KDMP✨",
        "KDMP🎉",
        "KDMP💯",
        "Koperasi Desa Merah Putih🔥",
        "Koperasi Desa Merah Putih👍",
        "Koperasi Desa Merah Putih👎",
        "Koperasi Desa Merah Putih💩",
        "Koperasi Desa Merah Putih🚀",
        "Koperasi Desa Merah Putih✨",
        "Koperasi Desa Merah Putih🎉",
        "Koperasi Desa Merah Putih💯",
        "program koperasi desa merah putih gagal",
        "program koperasi desa merah putih berhasil",
        "KDMP kritik",
        "koperasi desa viral",
    ],
    "Sekolah_Rakyat": [
        # Keyword utama
        "Sekolah Rakyat",
        "program sekolah rakyat",
        "sekolah rakyat gratis",
        "sekolah rakyat 2025",
        "sekolah rakyat 2026",
        "sekolah rakyat prabowo",
        "sekolah gratis rakyat",
        "sekolah rakyat pemerintah",
        # "sekolah unggulan rakyat",
        "program pendidikan sekolah rakyat",
        "sekolah rakyat indonesia",
        "sekolah rakyat gratis prabowo",
        # Keyword tambahan
        "sekolah rakyat asrama",
        "sekolah rakyat beasiswa",
        "sekolah rakyat viral",
        "sekolah rakyat kontroversi",
        "Kasus Sekolah Rakyat",
        # "Sekolah Rakyat Kasus",
        # Keyword lembaga & spesifik
        "sekolah rakyat Kemendikdasmen",
        "sekolah rakyat daerah terpencil",
        "sekolah rakyat kurikulum",
        "sekolah rakyat pendaftaran",
        # Keyword opini publik
        "sekolah rakyat gagal",
        "sekolah rakyat berhasil",
        "sekolah rakyat positif",
        "sekolah rakyat negatif",
        "sekolah rakyat🔥",
        "sekolah rakyat👍",
        "sekolah rakyat👎",
        "sekolah rakyat💩",
        "sekolah rakyat🚀",
        "sekolah rakyat✨",
        "sekolah rakyat🎉",
        "sekolah rakyat💯",
        "program sekolah rakyat gagal",
        "program sekolah rakyat berhasil",
        "sekolah rakyat kritik",
        "sekolah rakyat kualitas",
        "sekolah rakyat guru",
    ],
}

# Hitung total keyword
total_keywords = sum(len(v) for v in TOPICS.values())
print("=" * 60)
print("[OK] KONFIGURASI SELESAI")
print(f"[INFO] Topik: {len(TOPICS)} topik")
print(f"[INFO] Keywords: {total_keywords} variasi keyword")
print("=" * 60)

for topic, keywords in TOPICS.items():
    print(f"\n[TOPIK] {topic}: {len(keywords)} keywords")
    for kw in keywords:
        print(f"   - {kw}")
