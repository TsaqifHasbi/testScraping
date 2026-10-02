import sys

file_path = 'c:\\Users\\Asus\\OneDrive\\Documents\\Project_Streamlit\\cobaAPI\\dashboard\\poc\\data\\mock_provider.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """    from dashboard.poc.ingestion.youtube_scraper import fetch_youtube_data
    from dashboard.poc.ingestion.news_scraper import fetch_news_data
    from dashboard.poc.ingestion.threads_scraper import fetch_threads_data
    from dashboard.poc.ingestion.instagram_scraper import fetch_instagram_data

    # Kita batasi agar request API tidak terlalu lama
    max_per_platform = min(50, max(20, n_rows // 4))
    
    youtube_data = fetch_youtube_data(keyword, max_results=max_per_platform)
    news_data = fetch_news_data(keyword, max_results=max_per_platform)
    threads_data = fetch_threads_data(keyword, max_results=max_per_platform)
    instagram_data = fetch_instagram_data(keyword, max_results=max_per_platform)
    
    combined = youtube_data + news_data + threads_data + instagram_data"""

new_block = """    from dashboard.poc.ingestion.youtube_scraper import fetch_youtube_data
    from dashboard.poc.ingestion.news_scraper import fetch_news_data
    from dashboard.poc.ingestion.threads_scraper import fetch_threads_data
    from dashboard.poc.ingestion.instagram_scraper import fetch_instagram_data
    from dashboard.poc.ingestion.twitter_scraper import fetch_twitter_data

    # Kita batasi agar request API tidak terlalu lama
    max_per_platform = min(50, max(20, n_rows // 5))
    
    youtube_data = fetch_youtube_data(keyword, max_results=max_per_platform)
    news_data = fetch_news_data(keyword, max_results=max_per_platform)
    threads_data = fetch_threads_data(keyword, max_results=max_per_platform)
    instagram_data = fetch_instagram_data(keyword, max_results=max_per_platform)
    twitter_data = fetch_twitter_data(keyword, max_results=max_per_platform)
    
    combined = youtube_data + news_data + threads_data + instagram_data + twitter_data"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success patch twitter into mock_provider")
else:
    print("Block not found!")
