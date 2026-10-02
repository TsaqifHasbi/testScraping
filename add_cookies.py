import sys

file_path = 'c:\\Users\\Asus\\OneDrive\\Documents\\Project_Streamlit\\cobaAPI\\.env'
with open(file_path, 'a', encoding='utf-8') as f:
    f.write("TWITTER_AUTH_TOKEN=\n")
    f.write("TWITTER_CT0=\n")

print("Added cookie placeholders to .env")
