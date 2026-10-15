import os
import sys
import re
import json
import time
import requests

url = "https://www.tiktok.com/@ampkpsu2/video/7695752035819457813"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

print(f"Testing requests on {url}...")
try:
    resp = requests.get(url, headers=headers, timeout=10)
    print("Status code:", resp.status_code)
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        # Find itemStruct or desc
        def find_desc(obj):
            if isinstance(obj, dict):
                if 'itemStruct' in obj:
                    return obj['itemStruct'].get('desc', '')
                for v in obj.values():
                    res = find_desc(v)
                    if res: return res
            return ''
        d = find_desc(data)
        print("Requests extracted desc length:", len(d))
        print("Ends with:", d[-60:] if d else 'NONE')
    else:
        print("No REHYDRATION script found via requests")
except Exception as e:
    print("Requests error:", e)
