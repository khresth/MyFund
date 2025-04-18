import praw
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os
from dotenv import load_dotenv
import time

MAX_POSTS = 500  
SUBREDDITS = ["investing", "stocks", "wallstreetbets"]  
POST_COUNT_THRESHOLD = 50  
REQUEST_DELAY = 2
TIME_WINDOW_HOURS = 168  

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def count_ticker_mentions(ticker):
    """Count mentions of a ticker across multiple subreddits"""
    try:
        time.sleep(REQUEST_DELAY)
        post_count = 0
        total_posts_checked = 0
        print(f"\nScanning for {ticker} across {SUBREDDITS}...")
        
        for subreddit in SUBREDDITS:
            print(f"Checking r/{subreddit}...")
            submissions = reddit.subreddit(subreddit).new(limit=MAX_POSTS)
            post_found = False
            for submission in submissions:
                post_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                time_diff = (datetime.now(timezone.utc) - post_time).total_seconds() / 3600
                if time_diff > TIME_WINDOW_HOURS:
                    print(f"Skipping post (too old, {time_diff:.1f} hours): {submission.title[:50]}...")
                    continue
                post_found = True
                total_posts_checked += 1
                print(f"Checking post ({time_diff:.1f} hours old): {submission.title[:50]}...")
                text = f"{submission.title} {submission.selftext}".lower()
                count = text.count(ticker.lower())
                if count > 0:
                    print(f"Found {count} mention(s) in r/{subreddit}: {submission.title[:50]}...")
                post_count += count
            
            if not post_found:
                print(f"No posts found within {TIME_WINDOW_HOURS} hours in r/{subreddit}.")
        
        if total_posts_checked == 0:
            print("No posts checked across all subreddits.")
        decision = "BUY" if post_count > POST_COUNT_THRESHOLD else "NEUTRAL"
        print(f"Total mentions for {ticker}: {post_count} (across {total_posts_checked} posts) -> Decision: {decision}")
        return decision, post_count

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return "ERROR", 0

def update_database():
    """Update sentiment table with analysis results"""
    DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment (
                ticker TEXT PRIMARY KEY,
                post_count INT,
                sentiment_score REAL,
                last_updated TEXT
            )
            """)
            cursor.execute("SELECT ticker FROM stocks")
            tickers = [row[0] for row in cursor.fetchall()]
            
            if not tickers:
                print("No tickers found in stocks table.")
                return
            
            updated_count = 0
            for ticker in tickers:
                decision, post_count = count_ticker_mentions(ticker)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO sentiment 
                    (ticker, post_count, sentiment_score, last_updated)
                    VALUES (?, ?, ?, ?)
                    """,
                    (ticker, post_count, post_count, datetime.now(timezone.utc).isoformat())
                )
                updated_count += 1

            conn.commit()
            print(f"\nUpdated {updated_count}/{len(tickers)} stocks in sentiment table")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_database()