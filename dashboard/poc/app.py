"""
PoC Dashboard — Analisis Sentimen & SNA Lintas Platform
========================================================

Aplikasi Streamlit satu halaman untuk proof-of-concept dashboard
riset opini publik. Mendukung pencarian kata kunci dan menampilkan
9 tab visualisasi dengan data sintetis serta integrasi data mentah.

Cara menjalankan:
    streamlit run dashboard/poc/app.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# ── Path setup agar import lokal berfungsi ────────────────────────────────────
_POC_DIR = Path(__file__).resolve().parent
if str(_POC_DIR) not in sys.path:
    sys.path.insert(0, str(_POC_DIR))

import pandas as pd
import streamlit as st

# ── Page config (HARUS dipanggil pertama, sebelum import komponen lain) ──────
st.set_page_config(
    page_title="PoC Dashboard Sentimen & SNA",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Force reload submodule agar hot-reload Streamlit tidak menahan cache lama ──
import importlib
import data.mock_provider
importlib.reload(data.mock_provider)
import components.charts
importlib.reload(components.charts)

# ── Import komponen setelah page config ───────────────────────────────────────
from data.mock_provider import (  # noqa: E402
    PLATFORMS,
    get_emotion_distribution,
    get_issue_diffusion,
    get_mentions_trend,
    get_news_sites,
    get_overview_metrics,
    get_platform_sentiment,
    get_popular_terms_table,
    get_sna_graph,
    get_top_emoji,
    get_top_influencers,
    get_top_issues,
    get_viral_content,
    get_wordcloud_data,
    get_raw_scraped_data,
)
from components.charts import (  # noqa: E402
    EMOTION_COLORS,
    PLATFORM_COLORS,
    SENTIMENT_COLORS,
    render_diffusion_chart,
    render_emoji_table,
    render_emotion_bar,
    render_influencer_list,
    render_metric_cards,
    render_news_sites_table,
    render_platform_sentiment_card,
    render_sentiment_gauge,
    render_sentiment_pie,
    render_sna_graph,
    render_top_issues,
    render_trend_chart,
    render_viral_content,
    render_wordcloud,
)


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    /* ── Font import ────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

    html, body {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header styling ─────────────────────────── */
    .dashboard-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 8px 32px rgba(67, 56, 202, 0.15);
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #e0e7ff;
    }
    .dashboard-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #a5b4fc;
    }

    /* ── Search bar ─────────────────────────────── */
    .search-section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    /* ── Empty state ────────────────────────────── */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #64748b;
    }
    .empty-state .icon {
        font-size: 72px;
        margin-bottom: 12px;
    }
    .empty-state h2 {
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .empty-state p {
        color: #64748b;
        font-size: 15px;
        max-width: 480px;
        margin: 0 auto;
    }

    /* ── Tab styling tweaks ─────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        font-size: 13px;
    }

    /* ── Metric card tweaks ─────────────────────── */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    /* ── Info badge for keyword ─────────────────── */
    .keyword-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(99, 102, 241, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="dashboard-header">
        <h1 style='display:flex; align-items:center; gap:8px;'><span class='material-symbols-rounded' style='font-size:32px;'>dashboard</span> Dashboard Analisis Sentimen & SNA Lintas Platform</h1>
        <p>Proof-of-Concept · Tugas Akhir Teknik Informatika · Data Sintetis</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════

# Inisialisasi state
if "keyword" not in st.session_state:
    st.session_state["keyword"] = ""

st.markdown('<div class="search-section">', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    search_input = st.text_input(
        ":material/search: Kata Kunci Pencarian",
        placeholder='Contoh: "Sekolah Rakyat", "MBG", "KDMP"',
        label_visibility="collapsed",
        key="search_input",
    )
with col_btn:
    search_clicked = st.button(
        ":material/search: Cari",
        use_container_width=True,
        type="primary",
    )
st.markdown("</div>", unsafe_allow_html=True)

# Update keyword di session_state
if search_clicked and search_input.strip():
    st.session_state["keyword"] = search_input.strip()

keyword: str = st.session_state["keyword"]


# ══════════════════════════════════════════════════════════════════════════════
# EMPTY STATE — sebelum pencarian pertama
# ══════════════════════════════════════════════════════════════════════════════

if not keyword:
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon"><span class='material-symbols-rounded' style='font-size:64px;'>search</span></div>
            <h2>Masukkan Kata Kunci untuk Memulai</h2>
            <p>
                Ketik kata kunci di kotak pencarian di atas, lalu tekan <b>Cari</b>
                untuk menampilkan dashboard analisis sentimen dan Social Network Analysis
                lintas platform.
            </p>
            <p style="margin-top:12px; font-size:13px;">
                Contoh kata kunci: <code>Sekolah Rakyat</code>, <code>MBG</code>,
                <code>Makan Bergizi Gratis</code>, <code>KDMP</code>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD — ditampilkan setelah keyword terisi
# ══════════════════════════════════════════════════════════════════════════════

# Badge keyword aktif
st.markdown(
    f'<div class="keyword-badge" style="display:inline-flex; align-items:center; gap:6px;"><span class="material-symbols-rounded" style="font-size:16px;">label</span> Kata Kunci: {keyword}</div>',
    unsafe_allow_html=True,
)

# ── 9 Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    ":material/bar_chart: Overview",
    ":material/trending_up: Trend",
    ":material/forum: Sentimen per Platform",
    ":material/mood: Emosi & Ikon",
    ":material/hub: Social Network Analysis",
    ":material/newspaper: Isu & Difusi",
    ":material/star: Influencer & Konten Viral",
    ":material/cloud: Awan Kata & Tagar",
    ":material/database: Data Mentah",
])


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 1: OVERVIEW                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab1:
    st.markdown("### :material/bar_chart: Ringkasan Metrik")
    metrics = get_overview_metrics(keyword)
    render_metric_cards(metrics)

    st.markdown("---")
    col_pie, col_gauge = st.columns(2)
    with col_pie:
        render_sentiment_pie(metrics)
    with col_gauge:
        render_sentiment_gauge(metrics)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 2: TREND                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab2:
    st.markdown("### :material/trending_up: Tren Mention (30 Hari Terakhir)")

    trend_channel = get_mentions_trend(keyword, "channel")
    render_trend_chart(trend_channel, "Tren Mention per Platform", PLATFORM_COLORS)

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        trend_sentiment = get_mentions_trend(keyword, "sentiment")
        render_trend_chart(trend_sentiment, "Tren Mention per Sentimen", SENTIMENT_COLORS)
    with col_t2:
        trend_emotion = get_mentions_trend(keyword, "emotion")
        render_trend_chart(trend_emotion, "Tren Mention per Emosi", EMOTION_COLORS)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 3: SENTIMEN PER PLATFORM                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab3:
    st.markdown("### :material/forum: Breakdown Sentimen per Platform")
    st.caption("Distribusi sentimen (Positif / Negatif / Netral) untuk setiap platform media sosial dan berita online.")

    # Grid 3 kolom untuk 7 platform
    platforms_list = PLATFORMS
    rows = [platforms_list[i:i + 3] for i in range(0, len(platforms_list), 3)]

    for row_platforms in rows:
        cols = st.columns(len(row_platforms))
        for col, platform in zip(cols, row_platforms):
            with col:
                sentiment_data = get_platform_sentiment(keyword, platform)
                render_platform_sentiment_card(platform, sentiment_data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 4: EMOSI & EMOJI                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab4:
    st.markdown("### :material/mood: Distribusi Emosi & Ikon")

    col_emo, col_emoji = st.columns([3, 2])

    with col_emo:
        emotion_df = get_emotion_distribution(keyword)
        render_emotion_bar(emotion_df)

    with col_emoji:
        emoji_df = get_top_emoji(keyword)
        render_emoji_table(emoji_df)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 5: SOCIAL NETWORK ANALYSIS                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab5:
    st.markdown("### :material/hub: Social Network Analysis (SNA)")
    st.caption(
        "Graf interaktif menampilkan relasi antar pengguna. "
        "Ukuran node merepresentasikan skor sentralitas (degree centrality). "
        "Warna node sesuai kategori sentimen atau emosi dominan."
    )

    col_sna1, col_sna2 = st.columns(2)

    with col_sna1:
        G_sent = get_sna_graph(keyword, "sentiment")
        render_sna_graph(G_sent, ":material/radio_button_checked: SNA berdasarkan Sentimen", SENTIMENT_COLORS)

    with col_sna2:
        G_emo = get_sna_graph(keyword, "emotion")
        render_sna_graph(G_emo, ":material/palette: SNA berdasarkan Emosi", EMOTION_COLORS)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 6: ISU & DIFUSI                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab6:
    st.markdown("### :material/newspaper: Isu Utama & Pola Difusi Lintas Platform")

    col_issues, col_news = st.columns([3, 2])

    with col_issues:
        issues = get_top_issues(keyword)
        render_top_issues(issues)

    with col_news:
        news_df = get_news_sites(keyword)
        render_news_sites_table(news_df)

    st.markdown("---")
    st.markdown("#### :material/cell_tower: Difusi Isu Lintas Platform (Top 3 Isu)")
    diffusion_df = get_issue_diffusion(keyword)
    render_diffusion_chart(diffusion_df)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 7: INFLUENCER & KONTEN VIRAL                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab7:
    st.markdown("### :material/star: Top Pemengaruh & Konten Viral")
    st.caption("Pilih tab platform di bawah untuk melihat influencer dan konten viral per platform.")

    # Sub-tabs per platform (tanpa Berita Online)
    influencer_platforms = ["X/Twitter", "Facebook", "Instagram", "YouTube", "TikTok", "Threads"]
    sub_tabs = st.tabs([f":material/alternate_email: {p}" if p == "X/Twitter" else f":material/thumb_up: {p}" if p == "Facebook" else f":material/photo_camera: {p}" if p == "Instagram" else f":material/play_circle: {p}" if p == "YouTube" else f":material/music_note: {p}" if p == "TikTok" else f":material/forum: {p}" for p in influencer_platforms])

    for sub_tab, platform in zip(sub_tabs, influencer_platforms):
        with sub_tab:
            col_inf, col_viral = st.columns(2)

            with col_inf:
                inf_df = get_top_influencers(keyword, platform)
                render_influencer_list(inf_df, platform)

            with col_viral:
                viral_df = get_viral_content(keyword, platform)
                render_viral_content(viral_df, platform)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 8: AWAN KATA & TAGAR                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab8:
    st.markdown("### :material/cloud: Awan Kata & Tagar")

    term_freq = get_wordcloud_data(keyword, "term")
    render_wordcloud(term_freq, ":material/cloud: Awan Term — Seluruh Platform")

    st.markdown("---")

    hashtag_freq = get_wordcloud_data(keyword, "hashtag")
    render_wordcloud(hashtag_freq, ":material/tag: Awan Tagar — Seluruh Platform")

    st.markdown("---")

    st.markdown("#### :material/list_alt: Tagar & Term Populer Lintas Platform")
    popular_df = get_popular_terms_table(keyword)

    # Tampilkan dengan format yang rapi
    col_term, col_hash = st.columns(2)
    with col_term:
        st.markdown("##### :material/edit_document: Top Term")
        terms_only = popular_df[popular_df["type"] == "Term"].reset_index(drop=True)
        terms_only.index = range(1, len(terms_only) + 1)
        terms_only.index.name = "#"
        st.dataframe(
            terms_only[["term", "count", "platforms"]].rename(
                columns={"term": "Term", "count": "Frekuensi", "platforms": "Platform"}
            ),
            use_container_width=True,
        )

    with col_hash:
        st.markdown("##### :material/tag: Top Tagar")
        tags_only = popular_df[popular_df["type"] == "Hashtag"].reset_index(drop=True)
        tags_only.index = range(1, len(tags_only) + 1)
        tags_only.index.name = "#"
        st.dataframe(
            tags_only[["term", "count", "platforms"]].rename(
                columns={"term": "Tagar", "count": "Frekuensi", "platforms": "Platform"}
            ),
            use_container_width=True,
        )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ TAB 9: DATA MENTAH (RAW SCRAPED DATA)                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

st.sidebar.markdown("---")
if st.sidebar.button(":material/refresh: Refresh Data API (Hapus Cache)"):
    st.cache_data.clear()
    st.rerun()

with tab9:
    st.markdown("### :material/database: Data Mentah Hasil Scraping API")
    st.caption(
        "Tabel data mentah hasil scraping lintas platform. Anda dapat mengunggah file hasil scraping Anda sendiri (CSV / JSON) "
        "atau melihat data sintetis yang dihasilkan sistem untuk kata kunci ini."
    )

    # ── Upload Section ────────────────────────────────────────────────────────
    with st.expander(":material/upload: Unggah File Scraping Riil (CSV / JSON)", expanded=False):
        uploaded_file = st.file_uploader(
            "Pilih file data scraping (.csv atau .json)",
            type=["csv", "json"],
            help="Unggah file hasil scraper/API Anda. Kolom yang disarankan: platform, author, content, likes, shares, comments, url, dll."
        )

    raw_df: pd.DataFrame
    data_source_label: str = ""

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_json(uploaded_file)
            data_source_label = f"🟢 **Data Riil Diunggah:** `{uploaded_file.name}` ({len(raw_df):,} baris data)"
            st.success(f"Berhasil membaca {len(raw_df):,} baris data dari file: **{uploaded_file.name}**")
        except Exception as e:
            st.error(f"Gagal membaca file upload: {e}")
            raw_df = get_raw_scraped_data(keyword)
            data_source_label = f"⚡ **Data Sintetis Realistis (Fallback):** Kata kunci `{keyword}`"
    else:
        raw_df = get_raw_scraped_data(keyword)
        data_source_label = f"⚡ **Data Scraping Live:** Kata kunci `{keyword}` ({len(raw_df):,} baris data)"

    if raw_df.empty:
        st.warning("tidak ada data yang berhasil di tampilkan dari hasil scraping ataupun disambungkan ke API", icon="⚠️")
    else:
        st.markdown(
            f"""
            <div style="
                background: rgba(99, 102, 241, 0.1);
                border-left: 4px solid #6366f1;
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 13px;
                margin-bottom: 12px;
            ">
                {data_source_label}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Summary Metrics ───────────────────────────────────────────────────────
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Baris Data", f"{len(raw_df):,}")
        with col_m2:
            n_plat = raw_df["platform"].nunique() if "platform" in raw_df.columns else len(raw_df.columns)
            st.metric("Jumlah Platform" if "platform" in raw_df.columns else "Total Kolom", f"{n_plat}")
        with col_m3:
            if "sentiment" in raw_df.columns:
                pos_ratio = (raw_df["sentiment"].str.lower() == "positif").mean() * 100
                st.metric("Rasio Sentimen Positif", f"{pos_ratio:.1f}%")
            else:
                st.metric("Kolom Terdeteksi", f"{len(raw_df.columns)}")
        with col_m4:
            total_eng = 0
            for col_name in ["likes", "shares", "comments"]:
                if col_name in raw_df.columns and pd.api.types.is_numeric_dtype(raw_df[col_name]):
                    total_eng += raw_df[col_name].sum()
            st.metric("Total Engagement", f"{int(total_eng):,}")

        st.markdown("---")

        # ── Filter & Search Section ───────────────────────────────────────────────
        st.markdown("##### :material/search: Filter & Pencarian Cepat")
        # Menggunakan 3 kolom: Sentimen (1), Emosi (1), dan Cari Teks (2, lebih lebar)
        f_col1, f_col2, f_col3 = st.columns([1, 1, 2])

        df_filtered = raw_df.copy()

        with f_col1:
            if "sentiment" in raw_df.columns:
                available_sentiments = ["Semua"] + sorted(list(raw_df["sentiment"].dropna().astype(str).unique()))
                selected_sentiment = st.selectbox(
                    "Sentimen",
                    options=available_sentiments,
                    index=0,
                    key="filter_raw_sentiment",
                )
                if selected_sentiment != "Semua":
                    df_filtered = df_filtered[df_filtered["sentiment"] == selected_sentiment]

        with f_col2:
            if "emotion" in raw_df.columns:
                available_emotions = ["Semua"] + sorted(list(raw_df["emotion"].dropna().astype(str).unique()))
                selected_emotion = st.selectbox(
                    "Emosi",
                    options=available_emotions,
                    index=0,
                    key="filter_raw_emotion",
                )
                if selected_emotion != "Semua":
                    df_filtered = df_filtered[df_filtered["emotion"] == selected_emotion]

        with f_col3:
            search_query = st.text_input(
                "Cari Teks / Konten",
                placeholder="Ketik kata kunci untuk mencari di dalam tabel...",
                key="filter_raw_search",
            )
            if search_query:
                # Cari di kolom string manapun (content, text, author, dll.)
                text_cols = [c for c in df_filtered.columns if df_filtered[c].dtype == object]
                if text_cols:
                    mask = df_filtered[text_cols].apply(
                        lambda col: col.astype(str).str.contains(search_query, case=False, na=False)
                    ).any(axis=1)
                    df_filtered = df_filtered[mask]

        # ── Separate Tabs Per Platform ────────────────────────────────────────────
        if "raw_data_pages" not in st.session_state:
            st.session_state.raw_data_pages = {}

        if "platform" in df_filtered.columns:
            platforms_in_data = ["YouTube", "Berita Online", "Instagram", "Threads", "X/Twitter", "TikTok"]
        else:
            platforms_in_data = ["Data"]
    
        tabs = st.tabs([f"{p}" for p in platforms_in_data])
    
        for i, plat in enumerate(platforms_in_data):
            with tabs[i]:
                df_plat = df_filtered[df_filtered["platform"] == plat] if "platform" in df_filtered.columns else df_filtered
            
                # Fallback jika data lama (cache) masih mengandung 'shares' alih-alih 'views'
                if plat == "YouTube" and "shares" in df_plat.columns:
                    df_plat = df_plat.rename(columns={"shares": "views"})
                
                # Hapus kolom yang semuanya NaN/kosong untuk platform ini (agar beda field)
                df_plat = df_plat.dropna(axis=1, how='all')
            
                # Reset index agar tabel mulai dari 1, bukan dari index aslinya (misal 50)
                df_plat = df_plat.reset_index(drop=True)
                df_plat.index = df_plat.index + 1
            
                # Pagination setup
                page_key = f"page_raw_{plat}"
                if page_key not in st.session_state.raw_data_pages:
                    st.session_state.raw_data_pages[page_key] = 1
                
                items_per_page = 15
                total_pages = (len(df_plat) - 1) // items_per_page + 1 if len(df_plat) > 0 else 1
            
                if st.session_state.raw_data_pages[page_key] > total_pages:
                    st.session_state.raw_data_pages[page_key] = max(1, total_pages)
                
                current_page = st.session_state.raw_data_pages[page_key]
                start_idx = (current_page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                df_page = df_plat.iloc[start_idx:end_idx]
            
                st.markdown(f"Menampilkan **{start_idx + 1}** - **{min(end_idx, len(df_plat))}** dari **{len(df_plat):,}** baris data pada platform {plat}:")
            
                column_config = {}
                if "url" in df_page.columns:
                    column_config["url"] = st.column_config.LinkColumn("Tautan", display_text="Buka Link")
                if "likes" in df_page.columns:
                    column_config["likes"] = st.column_config.NumberColumn("Likes", format="%d")
                if "views" in df_page.columns:
                    column_config["views"] = st.column_config.NumberColumn("Views", format="%d")
                if "shares" in df_page.columns:
                    column_config["shares"] = st.column_config.NumberColumn("Shares", format="%d")
                if "comments" in df_page.columns:
                    column_config["comments"] = st.column_config.NumberColumn("Comments", format="%d")
                
                st.dataframe(
                    df_page,
                    use_container_width=True,
                    column_config=column_config,
                    height=480,
                )
            
                # Pagination Buttons Bottom
                st.write("")
                def make_set_page(pk):
                    def set_page(page_num):
                        st.session_state.raw_data_pages[pk] = page_num
                    return set_page
            
                set_page_cb = make_set_page(page_key)
            
                window_start = max(1, current_page - 2)
                window_end = min(total_pages, window_start + 4)
                if window_end - window_start < 4:
                    window_start = max(1, window_end - 4)
                pages_to_show = list(range(window_start, window_end + 1))
            
                cols = st.columns([1.5, 1, 1, 1, 1, 1, 1.5])
                with cols[0]:
                    if current_page > 1:
                        st.button(":material/arrow_back: Prev", on_click=set_page_cb, args=(current_page - 1,), key=f"prev_{plat}", use_container_width=True)
                for j, p in enumerate(pages_to_show):
                    with cols[j + 1]:
                        st.button(str(p), on_click=set_page_cb, args=(p,), type="primary" if p == current_page else "secondary", key=f"page_{plat}_{p}", use_container_width=True)
                with cols[6]:
                    if current_page < total_pages:
                        st.button("Next :material/arrow_forward:", on_click=set_page_cb, args=(current_page + 1,), key=f"next_{plat}", use_container_width=True)

        # ── Export Button ─────────────────────────────────────────────────────────
        c_btn1, c_btn2 = st.columns([2, 5])
        with c_btn1:
            csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label=":material/download: Unduh Data Terfilter (CSV)",
                data=csv_bytes,
                file_name=f"raw_data_{keyword}_{timestamp_str}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # ── Quick Post Inspector ──────────────────────────────────────────────────
        content_col = "content" if "content" in df_filtered.columns else "text" if "text" in df_filtered.columns else None
        if not df_filtered.empty and content_col:
            with st.expander(":material/search: Inspeksi Detail Satu Postingan", expanded=False):
                sample_indices = df_filtered.index.tolist()[:100]
                selected_idx = st.selectbox(
                    "Pilih baris untuk melihat isi lengkap:",
                    options=sample_indices,
                    format_func=lambda idx: f"[{df_filtered.loc[idx, 'platform'] if 'platform' in df_filtered.columns else '-'}] {str(df_filtered.loc[idx, 'author'] if 'author' in df_filtered.columns else 'User')} - {str(df_filtered.loc[idx, content_col])[:45]}...",
                )
                if selected_idx is not None:
                    item = df_filtered.loc[selected_idx]
                    st.markdown(f"**Platform:** `{item.get('platform', '-')}` | **Penulis:** `{item.get('author', '-')} ({item.get('handle', '-')})` | **Waktu:** `{item.get('created_at', '-')}`")
                    if "sentiment" in item or "emotion" in item:
                        st.markdown(f"**Sentimen:** `{item.get('sentiment', '-')}` | **Emosi:** `{item.get('emotion', '-')}`")
                    st.info(item.get(content_col, ""))
                    if "likes" in item or "shares" in item or "comments" in item:
                        st.caption(f":material/favorite: Likes: {item.get('likes', 0):,} | :material/share: Shares: {item.get('shares', 0):,} | :material/comment: Comments: {item.get('comments', 0):,}")


# ══════════════════════════════════════════════════════════════════════════╗
# ║ FOOTER                                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

st.markdown("---")
st.markdown(
        """
        <div style="text-align:center; color:#64748b; font-size:12px; padding:12px 0;">
            <b>PoC Dashboard Sentimen & SNA Lintas Platform</b><br>
            Tugas Akhir · S1 Teknik Informatika · Data yang ditampilkan adalah data sintetis untuk keperluan proof-of-concept.<br>
            Dibangun dengan Streamlit + Plotly + Pyvis + WordCloud
        </div>
        """,
        unsafe_allow_html=True,
)
