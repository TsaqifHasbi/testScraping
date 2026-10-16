"""
Social Network Analysis (SNA) by Sentiment Engine
Tugas Akhir: SNA by Sentiment dengan Deep Learning IndoBERT
Referensi: Drone Emprit Architecture + Dashboard Monitoring Kementerian PU
"""

import os
import sys
import re
import json
import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict, Counter

# Encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ENRICHED_PATH = os.path.join(DATA_DIR, 'enriched_corpus_for_sna.csv')
SNA_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(SNA_OUTPUT_DIR, exist_ok=True)

def build_sna_by_sentiment(topic_filter=None, min_interactions=2):
    """
    Membangun Graph SNA Multi-Platform Berdasarkan Sentimen IndoBERT:
    - Node: Akun / Tokoh / Media
    - Edge: Interaksi (Mentions, Co-occurrences, Quotes)
    - Node Attributes: Sentimen Dominan (IndoBERT), Engagement, Volume, Centrality
    """
    print("=" * 75)
    print("🌐 MEMBANGUN SOCIAL NETWORK ANALYSIS (SNA) BY SENTIMENT (INDOBERT)")
    print("=" * 75)
    
    if not os.path.exists(ENRICHED_PATH):
        print(f"[!] File {ENRICHED_PATH} belum ada. Menjalankan batch inferensi...")
        from models.infer_sentiment import batch_infer_sentiment
        df = batch_infer_sentiment()
    else:
        df = pd.read_csv(ENRICHED_PATH, low_memory=False)
        
    if topic_filter:
        print(f"Filter Topik: {topic_filter}")
        df = df[df['topic'].astype(str).str.lower() == topic_filter.lower()].copy()
        
    print(f"Total baris data yang diproses ke dalam Graf SNA: {len(df):,}")
    
    G = nx.DiGraph() # Directed Graph untuk In-Degree (Influencer) & Out-Degree (Amplifier)
    
    # 1. Agregasi Node Profile (User Sentiments & Engagements)
    user_sentiment_scores = defaultdict(list)
    user_platforms = {}
    user_engagements = defaultdict(int)
    user_post_counts = defaultdict(int)
    
    # Regex untuk mencari mention (@username) di dalam teks asli
    mention_pattern = re.compile(r'@([A-Za-z0-9_\.]+)')
    
    edges_dict = defaultdict(lambda: {'weight': 0, 'sentiments': []})
    
    print("Mengekstraksi simpul (nodes) dan relasi interaksi (edges)...")
    for _, row in df.iterrows():
        source_user = str(row.get('user_id', '')).strip()
        if not source_user or source_user == 'nan':
            source_user = f"{row.get('platform', 'Web')}_User"
            
        raw_text = str(row.get('raw_content', ''))
        sentiment_label = str(row.get('predicted_sentiment', 'Netral'))
        score = float(row.get('sentiment_score', 0.0) if pd.notna(row.get('sentiment_score')) else 0.0)
        eng = int(row.get('total_engagement', 0) if pd.notna(row.get('total_engagement')) else 0)
        platform = str(row.get('platform', 'SocialMedia'))
        
        user_sentiment_scores[source_user].append(score)
        user_platforms[source_user] = platform
        user_engagements[source_user] += eng
        user_post_counts[source_user] += 1
        
        # Cari target mention
        mentions = mention_pattern.findall(raw_text)
        for target in mentions:
            target_user = target.strip()
            if target_user and target_user.lower() != source_user.lower():
                edge_key = (source_user, target_user)
                edges_dict[edge_key]['weight'] += 1
                edges_dict[edge_key]['sentiments'].append(sentiment_label)
                
    # 2. Tambahkan Nodes ke NetworkX
    print(f"Menambahkan {len(user_sentiment_scores):,} simpul ke graf...")
    for user, scores in user_sentiment_scores.items():
        avg_score = float(np.mean(scores))
        if avg_score > 0.15:
            dom_sent = 'Positif'
            color = '#2ecc71' # Hijau
        elif avg_score < -0.15:
            dom_sent = 'Negatif'
            color = '#e74c3c' # Merah
        else:
            dom_sent = 'Netral'
            color = '#95a5a6' # Abu-abu
            
        G.add_node(
            user,
            platform=user_platforms.get(user, 'SocialMedia'),
            sentiment=dom_sent,
            sentiment_score=round(avg_score, 3),
            total_engagement=user_engagements[user],
            post_count=user_post_counts[user],
            color=color
        )
        
    # 3. Tambahkan Edges
    print(f"Menambahkan {len(edges_dict):,} relasi interaksi...")
    for (src, tgt), data in edges_dict.items():
        if data['weight'] >= min_interactions or G.has_node(tgt):
            if not G.has_node(tgt):
                G.add_node(tgt, platform='Mentioned', sentiment='Netral', sentiment_score=0.0, total_engagement=0, post_count=0, color='#95a5a6')
            
            # Dominant edge sentiment
            most_common_sent = Counter(data['sentiments']).most_common(1)[0][0]
            G.add_edge(src, tgt, weight=data['weight'], sentiment=most_common_sent)
            
    print(f"\n📊 Struktur Graf SNA Berhasil Dibangun:")
    print(f"   • Total Simpul (Nodes) : {G.number_of_nodes():,} entitas")
    print(f"   • Total Sisi (Edges)   : {G.number_of_edges():,} koneksi")
    
    # 4. Hitung Metrik Sentralitas SNA (Drone Emprit standard)
    print("\nMenghitung metrik sentralitas SNA...")
    in_degrees = dict(G.in_degree(weight='weight'))
    out_degrees = dict(G.out_degree(weight='weight'))
    
    # Simpan atribut ke node
    nx.set_node_attributes(G, in_degrees, 'in_degree')
    nx.set_node_attributes(G, out_degrees, 'out_degree')
    
    # Top Influencer (In-Degree tertinggi)
    top_influencers = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:15]
    print("\n🌟 TOP 10 PEMENGARUH UTAMA (TOP INFLUENCERS BY IN-DEGREE):")
    print(f"{'No':<3} {'Username / Akun':<30} {'In-Degree':>10} {'Sentimen Dominan':>18}")
    print("-" * 65)
    for i, (u, score) in enumerate(top_influencers[:10], 1):
        sent = G.nodes[u].get('sentiment', 'Netral')
        print(f"{i:<3} {u:<30} {score:>10} {sent:>18}")
        
    # 5. Ekspor Graf untuk Visualisasi Gephi & Dashboard
    prefix = f"{topic_filter.lower()}_" if topic_filter else "all_topics_"
    gexf_path = os.path.join(SNA_OUTPUT_DIR, f'{prefix}sna_by_sentiment.gexf')
    nx.write_gexf(G, gexf_path)
    print(f"\n💾 File Gephi (.gexf) siap pakai: {gexf_path}")
    
    # Ekspor Ringkasan JSON untuk Web Dashboard / Streamlit
    json_path = os.path.join(SNA_OUTPUT_DIR, f'{prefix}sna_summary.json')
    top_nodes_data = []
    for u, score in top_influencers[:25]:
        top_nodes_data.append({
            'user': u,
            'in_degree': int(score),
            'out_degree': int(out_degrees.get(u, 0)),
            'sentiment': G.nodes[u].get('sentiment', 'Netral'),
            'platform': G.nodes[u].get('platform', 'SocialMedia'),
            'engagement': int(G.nodes[u].get('total_engagement', 0))
        })
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'top_influencers': top_nodes_data
        }, f, indent=4)
    print(f"💾 File Ringkasan JSON tersimpan: {json_path}")
    print("=" * 75)
    return G

if __name__ == '__main__':
    build_sna_by_sentiment()
