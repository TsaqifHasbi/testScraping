"""
Mock Data Provider untuk PoC Dashboard Sentimen & SNA
=====================================================

Modul ini menghasilkan data sintetis realistis untuk keperluan proof-of-concept.
Setiap fungsi menggunakan hash(keyword) sebagai random seed agar hasilnya
konsisten dan reproducible untuk kata kunci yang sama.

CATATAN INTEGRASI DATA ASLI:
─────────────────────────────
Saat integrasi data asli, ganti isi setiap fungsi dengan query/inference
yang sesuai, TANPA mengubah signature atau return type. Lihat docstring
masing-masing fungsi untuk detail skema data asli yang akan digunakan.
"""

from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta
from typing import Literal

import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# KONSTANTA
# ══════════════════════════════════════════════════════════════════════════════

PLATFORMS: list[str] = [
    "Berita Online", "X/Twitter", "Facebook",
    "Instagram", "YouTube", "TikTok", "Threads",
]

EMOTIONS_EKMAN: list[str] = [
    "Senang", "Sedih", "Marah", "Takut",
    "Jijik", "Terkejut", "Percaya", "Antisipasi",
]

SENTIMENTS: list[str] = ["Positif", "Negatif", "Netral"]

_EDUCATION_TERMS: list[str] = [
    "pendidikan", "sekolah", "guru", "siswa", "murid", "kurikulum",
    "belajar", "mengajar", "kelas", "pelajaran", "ujian", "rapor",
    "kampus", "universitas", "dosen", "mahasiswa", "beasiswa",
    "literasi", "numerasi", "inklusi", "akreditasi", "sertifikasi",
]

_GOVERNMENT_TERMS: list[str] = [
    "pemerintah", "kebijakan", "program", "anggaran", "subsidi",
    "menteri", "presiden", "kementerian", "regulasi", "sosialisasi",
    "implementasi", "evaluasi", "transparansi", "akuntabilitas",
    "APBN", "dana BOS", "DAK", "bantuan sosial",
]

_SEKOLAH_RAKYAT_TERMS: list[str] = [
    "Sekolah Rakyat", "MBG", "Makan Bergizi Gratis", "KDMP",
    "Kampanye Damai Menulis Membaca", "gizi", "nutrisi",
    "stunting", "wajib belajar", "akses pendidikan", "pemerataan",
    "infrastruktur sekolah", "guru honorer", "kurikulum merdeka",
    "digitalisasi", "transformasi pendidikan", "kualitas pendidikan",
    "zonasi", "PAUD", "SD", "SMP", "SMA",
]

_COMMON_HASHTAGS: list[str] = [
    "#SekolahRakyat", "#MBG", "#MakanBergiziGratis", "#KDMP",
    "#PendidikanIndonesia", "#GuruHebat", "#AnakBangsa",
    "#IndonesiaMaju", "#PendidikanBerkualitas", "#WajibBelajar",
    "#MerdekaBelajar", "#KurikulumMerdeka", "#DigitalisasiPendidikan",
    "#BeasiswaPendidikan", "#SekolahGratis", "#PendidikanMerata",
    "#GiziAnak", "#StuntingFree", "#GenerasiEmas", "#SDMUnggul",
    "#CerdasBerkarakter", "#IndonesiaEmas2045", "#PendidikanGratis",
    "#BantuanPendidikan", "#ReformasiPendidikan",
]

_SAMPLE_EMOJIS: list[str] = [
    "👍", "❤️", "😊", "🙏", "👏", "🔥", "💪", "😢", "😡", "🤔",
    "✅", "🎓", "📚", "🏫", "🇮🇩", "⭐", "💯", "🤝", "😍", "🫡",
]

_NEWS_SITES: list[str] = [
    "detik.com", "kompas.com", "tempo.co", "liputan6.com",
    "tribunnews.com", "cnnindonesia.com", "tirto.id",
    "republika.co.id", "antaranews.com", "medcom.id",
    "suara.com", "okezone.com", "sindonews.com", "jpnn.com",
    "merdeka.com",
]

_INDONESIAN_NAMES: list[str] = [
    "Budi Santoso", "Siti Aminah", "Ahmad Fauzi", "Dewi Lestari",
    "Rizky Pratama", "Nur Hidayah", "Fajar Nugroho", "Ayu Kusuma",
    "Dimas Arya", "Putri Rahayu", "Andi Wijaya", "Ratna Sari",
    "Bambang Hermanto", "Lestari Wulandari", "Hendra Gunawan",
    "Fitri Handayani", "Agus Setiawan", "Maya Indah", "Rudi Hartono",
    "Wulan Permata", "Joko Susanto", "Kartika Dewi", "Surya Darma",
    "Nadia Putri", "Eko Prasetyo",
]

_HANDLE_PREFIXES: list[str] = [
    "info_", "berita_", "update_", "kabar_", "opini_",
    "edukasi_", "guru_", "dosen_", "aktivis_", "jurnalis_",
]

_ISSUE_TEMPLATES: list[str] = [
    "Implementasi {} di Daerah Terpencil",
    "Anggaran {} Dipertanyakan DPR",
    "Efektivitas {} dalam Meningkatkan Kualitas Pendidikan",
    "Polemik {} dan Respons Masyarakat",
    "Evaluasi Program {} Semester Pertama",
    "Tantangan Distribusi Logistik {}",
    "Dampak {} terhadap Angka Partisipasi Sekolah",
    "Dukungan Pemda untuk {}",
    "Kritik Akademisi terhadap {}",
    "Inovasi Teknologi dalam {}",
    "Transparansi Dana {}",
    "Peran Komunitas dalam Mendukung {}",
]

_VIRAL_TEMPLATES: list[str] = [
    "Thread panjang tentang pengalaman {} di sekolah kami...",
    "Begini kondisi nyata {} yang jarang diberitakan media 🧵",
    "Data terbaru menunjukkan dampak {} terhadap siswa Indonesia",
    "Cerita guru honorer soal {} yang bikin haru 😢",
    "BREAKING: Pemerintah umumkan perubahan kebijakan {} terbaru!",
    "Viral! Video siswa terima manfaat {} pertama kali 🎓",
    "Opini: Mengapa {} perlu dievaluasi secara menyeluruh",
    "Fakta menarik tentang {} yang belum banyak diketahui 📊",
    "Perbandingan {} Indonesia vs negara ASEAN lainnya",
    "Warga desa ini buktikan {} bisa ubah kualitas hidup anak",
]


# ══════════════════════════════════════════════════════════════════════════════
# UTILITAS INTERNAL
# ══════════════════════════════════════════════════════════════════════════════

def _seed(keyword: str) -> None:
    """Set random seed berdasarkan hash keyword untuk reproducibility."""
    seed_val = int(hashlib.md5(keyword.lower().encode()).hexdigest(), 16) & 0xFFFFFFFF
    random.seed(seed_val)
    np.random.seed(seed_val & 0x7FFFFFFF)


def _get_related_terms(keyword: str) -> list[str]:
    """Mengembalikan pool istilah yang relevan berdasarkan keyword pencarian."""
    kw_lower = keyword.lower()
    base = list(_EDUCATION_TERMS) + list(_GOVERNMENT_TERMS)
    if any(t in kw_lower for t in ["sekolah", "rakyat", "mbg", "kdmp", "makan", "gizi"]):
        base.extend(_SEKOLAH_RAKYAT_TERMS)
    base.append(keyword)
    return list(set(base))


def _make_handle(name: str, platform: str) -> str:
    """Buat handle/username realistis dari nama dan platform."""
    slug = name.lower().replace(" ", "")
    prefix = random.choice(_HANDLE_PREFIXES) if random.random() < 0.3 else ""
    suffix = str(random.randint(1, 999)) if random.random() < 0.5 else ""
    if platform in ("YouTube",):
        return f"{name} Channel"
    return f"@{prefix}{slug}{suffix}"


# ══════════════════════════════════════════════════════════════════════════════
# FUNGSI-FUNGSI DATA PUBLIK
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def get_overview_metrics(keyword: str) -> dict:
    """
    Mengembalikan metrik ringkasan dashboard.

    Returns
    -------
    dict
        Keys: volume (int), users (int), engagement (int), reach (int),
              sentiment_positive (float %), sentiment_negative (float %),
              sentiment_neutral (float %).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query aggregate ke tabel PostgreSQL:
        - volume  = COUNT(*) FROM posts WHERE keyword_match(content, :kw)
        - users   = COUNT(DISTINCT author_id) FROM posts ...
        - engagement = SUM(likes + shares + comments) FROM posts ...
        - reach   = SUM(estimated_reach) FROM posts ...
        - sentiment = proporsi dari tabel sentiment_labels
          (hasil inference model IndoBERT fine-tuned sentiment)
    """
    _seed(keyword)

    volume = random.randint(15_000, 350_000)
    users = random.randint(3_000, max(3_001, int(volume * 0.3)))
    engagement = random.randint(volume * 2, volume * 8)
    reach = random.randint(volume * 10, volume * 50)

    pos = random.uniform(0.25, 0.55)
    neg = random.uniform(0.10, 0.35)
    neu = round(1.0 - pos - neg, 3)

    return {
        "volume": volume,
        "users": users,
        "engagement": engagement,
        "reach": reach,
        "sentiment_positive": round(pos * 100, 1),
        "sentiment_negative": round(neg * 100, 1),
        "sentiment_neutral": round(neu * 100, 1),
    }


@st.cache_data(show_spinner=False)
def get_mentions_trend(
    keyword: str,
    dimension: Literal["channel", "sentiment", "emotion"],
) -> pd.DataFrame:
    """
    Mengembalikan data tren mention harian selama 30 hari terakhir.

    Parameters
    ----------
    keyword : str
        Kata kunci pencarian.
    dimension : {"channel", "sentiment", "emotion"}
        Dimensi pengelompokan: platform (channel), sentimen, atau emosi.

    Returns
    -------
    pd.DataFrame
        Kolom: date (datetime), category (str), count (int).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT DATE(created_at) as date,
               {dimension_column} as category,
               COUNT(*) as count
        FROM posts
        JOIN sentiment_labels USING (post_id)
        WHERE keyword_match(content, :kw)
          AND created_at >= NOW() - INTERVAL '30 days'
        GROUP BY date, category
        ORDER BY date
    """
    _seed(keyword + dimension)

    end_date = datetime.now().date()
    dates = [end_date - timedelta(days=i) for i in range(29, -1, -1)]

    if dimension == "channel":
        categories = PLATFORMS
    elif dimension == "sentiment":
        categories = SENTIMENTS
    else:
        categories = EMOTIONS_EKMAN[:6]  # 6 emosi utama untuk tren

    rows: list[dict] = []
    for cat in categories:
        base = random.randint(50, 800)
        for d in dates:
            noise = random.gauss(0, base * 0.2)
            # Simulasi tren naik-turun
            day_idx = dates.index(d)
            trend = base * (1 + 0.3 * np.sin(day_idx / 5))
            count = max(1, int(trend + noise))
            rows.append({"date": d, "category": cat, "count": count})

    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_platform_sentiment(keyword: str, platform: str) -> dict:
    """
    Mengembalikan breakdown sentimen untuk satu platform.

    Returns
    -------
    dict
        Keys: positive (float %), negative (float %), neutral (float %),
              total_mentions (int).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT sentiment_label, COUNT(*) as cnt
        FROM posts
        JOIN sentiment_labels USING (post_id)
        WHERE platform = :platform
          AND keyword_match(content, :kw)
        GROUP BY sentiment_label

        sentiment_label berasal dari inferensi model IndoBERT
        fine-tuned pada dataset sentimen Bahasa Indonesia.
    """
    _seed(keyword + platform)

    pos = random.uniform(0.20, 0.60)
    neg = random.uniform(0.10, 0.40)
    neu = round(1.0 - pos - neg, 3)
    if neu < 0:
        neu = 0.05
        total = pos + neg + neu
        pos, neg, neu = pos / total, neg / total, neu / total

    total_mentions = random.randint(500, 50_000)

    return {
        "positive": round(pos * 100, 1),
        "negative": round(neg * 100, 1),
        "neutral": round(neu * 100, 1),
        "total_mentions": total_mentions,
    }


@st.cache_data(show_spinner=False)
def get_emotion_distribution(keyword: str) -> pd.DataFrame:
    """
    Mengembalikan distribusi emosi berdasarkan klasifikasi Ekman (8 kelas).

    Returns
    -------
    pd.DataFrame
        Kolom: emotion (str), count (int), percentage (float).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT emotion_label as emotion, COUNT(*) as count
        FROM posts
        JOIN emotion_labels USING (post_id)
        WHERE keyword_match(content, :kw)
        GROUP BY emotion_label

        emotion_label berasal dari model IndoBERT fine-tuned pada
        dataset emosi Ekman Bahasa Indonesia (GoEmotions-ID atau
        dataset custom).
    """
    _seed(keyword + "emotion")

    counts = [random.randint(200, 5000) for _ in EMOTIONS_EKMAN]
    total = sum(counts)

    return pd.DataFrame({
        "emotion": EMOTIONS_EKMAN,
        "count": counts,
        "percentage": [round(c / total * 100, 1) for c in counts],
    })


@st.cache_data(show_spinner=False)
def get_top_emoji(keyword: str) -> pd.DataFrame:
    """
    Mengembalikan daftar emoji yang paling sering digunakan.

    Returns
    -------
    pd.DataFrame
        Kolom: emoji (str), count (int). Diurutkan descending.

    INTEGRASI DATA ASLI:
        Akan diganti dengan query regex extraction:
        SELECT emoji, COUNT(*) as count
        FROM (
            SELECT unnest(regexp_matches(content, :emoji_pattern, 'g')) as emoji
            FROM posts
            WHERE keyword_match(content, :kw)
        ) sub
        GROUP BY emoji
        ORDER BY count DESC
        LIMIT 15
    """
    _seed(keyword + "emoji")

    emojis = random.sample(_SAMPLE_EMOJIS, min(15, len(_SAMPLE_EMOJIS)))
    counts = sorted([random.randint(100, 8000) for _ in emojis], reverse=True)

    return pd.DataFrame({"emoji": emojis, "count": counts})


@st.cache_resource(show_spinner=False)
def get_sna_graph(
    keyword: str,
    mode: Literal["sentiment", "emotion"],
) -> nx.Graph:
    """
    Mengembalikan graf Social Network Analysis.

    Parameters
    ----------
    keyword : str
        Kata kunci pencarian.
    mode : {"sentiment", "emotion"}
        Mode pewarnaan node: berdasarkan sentimen atau emosi.

    Returns
    -------
    networkx.Graph
        Node attributes: label (str), group (str), centrality (float).
        Edge attributes: weight (float).

    INTEGRASI DATA ASLI:
        Akan diganti dengan konstruksi graf dari data interaksi:
        1. Query relasi interaksi (reply, retweet, mention) antar user:
           SELECT source_user, target_user, interaction_type, COUNT(*)
           FROM interactions
           WHERE keyword_match(content, :kw)
           GROUP BY source_user, target_user, interaction_type

        2. Node attributes diambil dari tabel users + sentiment/emotion
           mayoritas per user:
           SELECT user_id,
                  MODE() WITHIN GROUP (ORDER BY sentiment_label) as dominant_sentiment
           FROM posts JOIN sentiment_labels USING (post_id)
           GROUP BY user_id

        3. Sentralitas dihitung dengan NetworkX:
           nx.betweenness_centrality(G) atau nx.degree_centrality(G)
    """
    _seed(keyword + mode)

    G = nx.Graph()

    # Tentukan grup berdasarkan mode
    if mode == "sentiment":
        groups = SENTIMENTS
    else:
        groups = EMOTIONS_EKMAN[:6]

    # Buat 30-50 node
    n_nodes = random.randint(30, 50)
    names = random.sample(_INDONESIAN_NAMES, min(n_nodes, len(_INDONESIAN_NAMES)))
    if n_nodes > len(names):
        for i in range(n_nodes - len(names)):
            names.append(f"User_{i + 1}")

    for i, name in enumerate(names):
        G.add_node(
            i,
            label=name,
            group=random.choice(groups),
        )

    # Buat edges (model small-world-ish)
    n_edges = random.randint(n_nodes * 2, n_nodes * 4)
    for _ in range(n_edges):
        u = random.randint(0, n_nodes - 1)
        v = random.randint(0, n_nodes - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v, weight=round(random.uniform(0.1, 1.0), 2))

    # Hitung sentralitas
    centrality = nx.degree_centrality(G)
    for node_id, cent_val in centrality.items():
        G.nodes[node_id]["centrality"] = round(cent_val, 4)

    return G


@st.cache_data(show_spinner=False)
def get_top_issues(keyword: str) -> list[dict]:
    """
    Mengembalikan daftar isu utama yang teridentifikasi (ranked).

    Returns
    -------
    list[dict]
        Setiap dict: rank (int), title (str), mentions (int),
                     platforms (list[str]).

    INTEGRASI DATA ASLI:
        Akan diganti dengan hasil topic modeling / clustering:
        1. Jalankan BERTopic atau LDA pada korpus posts yang match keyword
        2. Ambil top-N cluster / topic
        3. Labelisasi otomatis atau manual per topik
        4. Hitung mention count per topik
        5. Identifikasi platform mana saja yang membahas topik tersebut
    """
    _seed(keyword + "issues")

    kw_short = keyword.split()[0] if keyword.split() else keyword
    templates = random.sample(_ISSUE_TEMPLATES, min(10, len(_ISSUE_TEMPLATES)))

    issues: list[dict] = []
    for i, tpl in enumerate(templates, start=1):
        n_platforms = random.randint(2, len(PLATFORMS))
        issues.append({
            "rank": i,
            "title": tpl.format(kw_short),
            "mentions": random.randint(500, 25_000),
            "platforms": random.sample(PLATFORMS, n_platforms),
        })

    # Sort by mentions descending, then re-rank
    issues.sort(key=lambda x: x["mentions"], reverse=True)
    for i, iss in enumerate(issues, start=1):
        iss["rank"] = i

    return issues


@st.cache_data(show_spinner=False)
def get_issue_diffusion(keyword: str) -> pd.DataFrame:
    """
    Mengembalikan data difusi isu lintas platform (small multiples).

    Returns
    -------
    pd.DataFrame
        Kolom: date (datetime), platform (str), issue (str), count (int).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT DATE(created_at) as date,
               platform,
               topic_label as issue,
               COUNT(*) as count
        FROM posts
        JOIN topic_labels USING (post_id)
        WHERE keyword_match(content, :kw)
          AND created_at >= NOW() - INTERVAL '30 days'
        GROUP BY date, platform, issue
        ORDER BY date

        topic_label berasal dari BERTopic / clustering model.
    """
    _seed(keyword + "diffusion")

    end_date = datetime.now().date()
    dates = [end_date - timedelta(days=i) for i in range(29, -1, -1)]

    # Ambil top 3 isu saja untuk diffusion chart
    issues = get_top_issues(keyword)[:3]
    _seed(keyword + "diffusion")  # Re-seed setelah call internal

    rows: list[dict] = []
    for iss in issues:
        for platform in PLATFORMS[:5]:  # 5 platform utama
            base = random.randint(10, 200)
            for d in dates:
                day_idx = dates.index(d)
                # Simulasi diffusion: mulai rendah, spike, lalu turun
                spike_day = random.randint(5, 20)
                if day_idx < spike_day:
                    val = base * (day_idx / spike_day)
                else:
                    val = base * max(0.2, 1 - (day_idx - spike_day) / 15)
                noise = random.gauss(0, val * 0.15)
                count = max(0, int(val + noise))
                rows.append({
                    "date": d,
                    "platform": platform,
                    "issue": iss["title"],
                    "count": count,
                })

    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_news_sites(keyword: str) -> pd.DataFrame:
    """
    Mengembalikan daftar situs berita yang paling banyak memberitakan.

    Returns
    -------
    pd.DataFrame
        Kolom: site (str), article_count (int), reach (int).
        Diurutkan descending by article_count.

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT domain as site,
               COUNT(*) as article_count,
               SUM(estimated_reach) as reach
        FROM posts
        WHERE platform = 'Berita Online'
          AND keyword_match(content, :kw)
        GROUP BY domain
        ORDER BY article_count DESC
        LIMIT 15
    """
    _seed(keyword + "news")

    sites = random.sample(_NEWS_SITES, min(12, len(_NEWS_SITES)))
    articles = sorted(
        [random.randint(10, 500) for _ in sites], reverse=True
    )
    reaches = [a * random.randint(5_000, 50_000) for a in articles]

    return pd.DataFrame({
        "site": sites,
        "article_count": articles,
        "reach": reaches,
    })


@st.cache_data(show_spinner=False)
def get_top_influencers(keyword: str, platform: str) -> pd.DataFrame:
    """
    Mengembalikan daftar top influencer / pemengaruh per platform.

    Returns
    -------
    pd.DataFrame
        Kolom: name (str), handle (str), followers (int),
               engagement_rate (float %), posts (int).
        Diurutkan descending by engagement_rate.

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT u.display_name as name,
               u.handle,
               u.follower_count as followers,
               AVG(p.engagement_score) / u.follower_count * 100 as engagement_rate,
               COUNT(p.post_id) as posts
        FROM users u
        JOIN posts p ON u.user_id = p.author_id
        WHERE p.platform = :platform
          AND keyword_match(p.content, :kw)
        GROUP BY u.user_id, u.display_name, u.handle, u.follower_count
        ORDER BY engagement_rate DESC
        LIMIT 10

        follower_count diambil dari data scraping profil pengguna.
    """
    _seed(keyword + platform + "influencer")

    n = min(10, len(_INDONESIAN_NAMES))
    names = random.sample(_INDONESIAN_NAMES, n)
    handles = [_make_handle(name, platform) for name in names]
    followers = [random.randint(1_000, 2_000_000) for _ in names]
    eng_rates = [round(random.uniform(0.5, 12.0), 2) for _ in names]
    posts = [random.randint(1, 50) for _ in names]

    df = pd.DataFrame({
        "name": names,
        "handle": handles,
        "followers": followers,
        "engagement_rate": eng_rates,
        "posts": posts,
    })

    return df.sort_values("engagement_rate", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_viral_content(keyword: str, platform: str) -> pd.DataFrame:
    """
    Mengembalikan konten paling viral per platform.

    Returns
    -------
    pd.DataFrame
        Kolom: content (str), author (str), likes (int),
               shares (int), comments (int), url (str).
        Diurutkan descending by total engagement (likes + shares + comments).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query:
        SELECT p.content,
               u.display_name as author,
               p.like_count as likes,
               p.share_count as shares,
               p.comment_count as comments,
               p.original_url as url
        FROM posts p
        JOIN users u ON p.author_id = u.user_id
        WHERE p.platform = :platform
          AND keyword_match(p.content, :kw)
        ORDER BY (p.like_count + p.share_count + p.comment_count) DESC
        LIMIT 10
    """
    _seed(keyword + platform + "viral")

    kw_short = keyword.split()[0] if keyword.split() else keyword
    n = min(10, len(_VIRAL_TEMPLATES))
    templates = random.sample(_VIRAL_TEMPLATES, n)
    names = random.sample(_INDONESIAN_NAMES, n)

    contents = [tpl.format(kw_short) for tpl in templates]
    likes = sorted([random.randint(500, 100_000) for _ in range(n)], reverse=True)
    shares = [random.randint(int(l * 0.1), int(l * 0.5)) for l in likes]
    comments = [random.randint(int(l * 0.05), int(l * 0.3)) for l in likes]
    urls = [f"https://{platform.lower().replace('/', '').replace(' ', '')}.example.com/post/{random.randint(10000, 99999)}" for _ in range(n)]

    return pd.DataFrame({
        "content": contents,
        "author": names,
        "likes": likes,
        "shares": shares,
        "comments": comments,
        "url": urls,
    })


@st.cache_data(show_spinner=False)
def get_wordcloud_data(
    keyword: str,
    scope: Literal["term", "hashtag"],
) -> dict[str, int]:
    """
    Mengembalikan frekuensi term atau hashtag untuk word cloud.

    Parameters
    ----------
    keyword : str
        Kata kunci pencarian.
    scope : {"term", "hashtag"}
        Jenis data: term biasa atau hashtag.

    Returns
    -------
    dict[str, int]
        Mapping term/hashtag → frekuensi.

    INTEGRASI DATA ASLI:
        Akan diganti dengan:
        - scope="term": TF-IDF atau raw term frequency dari preprocessing
          NLP (tokenisasi, stopword removal, stemming Bahasa Indonesia)
          pada seluruh posts yang match keyword.
        - scope="hashtag": Ekstraksi hashtag via regex (#\\w+) dari posts,
          lalu COUNT per hashtag.

        Query contoh (hashtag):
        SELECT hashtag, COUNT(*) as freq
        FROM (
            SELECT unnest(regexp_matches(content, '#(\\w+)', 'g')) as hashtag
            FROM posts WHERE keyword_match(content, :kw)
        ) sub
        GROUP BY hashtag ORDER BY freq DESC LIMIT 100
    """
    _seed(keyword + scope)

    if scope == "hashtag":
        pool = list(_COMMON_HASHTAGS)
        # Tambah hashtag dari keyword
        kw_hashtag = "#" + keyword.replace(" ", "")
        pool.append(kw_hashtag)
        n = min(40, len(pool))
        selected = random.sample(pool, n)
    else:
        pool = _get_related_terms(keyword)
        n = min(60, len(pool))
        selected = random.sample(pool, n)

    freq: dict[str, int] = {}
    for term in selected:
        freq[term] = random.randint(10, 5000)

    return freq


@st.cache_data(show_spinner=False)
def get_popular_terms_table(keyword: str) -> pd.DataFrame:
    """
    Mengembalikan tabel term & hashtag populer lintas platform.

    Returns
    -------
    pd.DataFrame
        Kolom: term (str), count (int), type (str: "Term"/"Hashtag"),
               platforms (str — comma-separated).

    INTEGRASI DATA ASLI:
        Akan diganti dengan query gabungan term frequency dan hashtag
        frequency yang di-aggregate lintas platform, dengan kolom platform
        menunjukkan di platform mana saja term tersebut muncul.
    """
    _seed(keyword + "popular_terms")

    terms_data = get_wordcloud_data(keyword, "term")
    hashtag_data = get_wordcloud_data(keyword, "hashtag")
    _seed(keyword + "popular_terms")  # Re-seed setelah call internal

    rows: list[dict] = []
    for term, count in sorted(terms_data.items(), key=lambda x: x[1], reverse=True)[:15]:
        n_plat = random.randint(2, len(PLATFORMS))
        plats = random.sample(PLATFORMS, n_plat)
        rows.append({
            "term": term,
            "count": count,
            "type": "Term",
            "platforms": ", ".join(plats),
        })

    for tag, count in sorted(hashtag_data.items(), key=lambda x: x[1], reverse=True)[:10]:
        n_plat = random.randint(2, len(PLATFORMS))
        plats = random.sample(PLATFORMS, n_plat)
        rows.append({
            "term": tag,
            "count": count,
            "type": "Hashtag",
            "platforms": ", ".join(plats),
        })

    df = pd.DataFrame(rows)
    return df.sort_values("count", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_raw_scraped_data(keyword: str, n_rows: int = 150) -> pd.DataFrame:
    """
    Mengembalikan data mentah hasil scraping riil (YouTube & News).
    Cache buster: 1
    """
    from dashboard.poc.ingestion.youtube_scraper import fetch_youtube_data
    from dashboard.poc.ingestion.news_scraper import fetch_news_data
    from dashboard.poc.ingestion.threads_scraper import fetch_threads_data
    from dashboard.poc.ingestion.instagram_scraper import fetch_instagram_data
    from dashboard.poc.ingestion.twitter_scraper import fetch_twitter_data
    from dashboard.poc.ingestion.tiktok_scraper import fetch_tiktok_data

    # Kita batasi agar request API tidak terlalu lama
    max_per_platform = min(50, max(20, n_rows // 5))
    
    youtube_data = fetch_youtube_data(keyword, max_results=max_per_platform)
    news_data = fetch_news_data(keyword, max_results=max_per_platform)
    threads_data = fetch_threads_data(keyword, max_results=max_per_platform)
    instagram_data = fetch_instagram_data(keyword, max_results=max_per_platform)
    twitter_data = fetch_twitter_data(keyword, max_results=max_per_platform)
    tiktok_data = fetch_tiktok_data(keyword, max_results=max_per_platform)
    
    combined = youtube_data + news_data + threads_data + instagram_data + twitter_data + tiktok_data
    
    if not combined:
        return pd.DataFrame(columns=[
            "post_id", "platform", "author", "handle", "created_at",
            "content", "sentiment", "emotion", "likes", "shares",
            "comments", "url"
        ])
    
    df = pd.DataFrame(combined)
    
    # Tambahkan mock sentiment dan emotion agar filter di UI dashboard tidak error
    _seed(keyword + "raw_scraped_data_mock_labels")
    if "sentiment" not in df.columns:
        df["sentiment"] = [random.choices(SENTIMENTS, weights=[0.45, 0.30, 0.25], k=1)[0] for _ in range(len(df))]
    if "emotion" not in df.columns:
        df["emotion"] = df["sentiment"].apply(
            lambda s: random.choice(["Senang", "Percaya", "Antisipasi"]) if s == "Positif" else
                      (random.choice(["Marah", "Sedih", "Takut", "Jijik"]) if s == "Negatif" else
                       random.choice(["Terkejut", "Antisipasi", "Percaya"]))
        )
        
    return df.sort_values("created_at", ascending=False).reset_index(drop=True)
