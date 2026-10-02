import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def reset_pool():
    from twscrape import API
    api = API()
    username = os.environ.get("TWITTER_USERNAME")
    
    # Force delete the old account state
    try:
        await api.pool.delete_account(username)
        print(f"Deleted old state for {username}")
    except Exception as e:
        print("Delete failed:", e)

if __name__ == "__main__":
    asyncio.run(reset_pool())
