import praw
from textblob import TextBlob
import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os
from dotenv import load_dotenv


MAX_POSTS = 5
SENTIMENT_THRESHOLD = 0.25
SUBREDDITS = ["investing", "stocks"]
REQUEST_DELAY = 2

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def analyze_sentiment(ticker):
    """Analyze sentiment for a given ticker"""
    try:
        time.sleep(REQUEST_DELAY)
        
        posts = []
        for subreddit in SUBREDDITS:
            try:
                submissions = reddit.subreddit(subreddit).search(
                    query=ticker,
                    limit=3,
                    time_filter="week"
                )
                for submission in submissions:
                    posts.append(f"{submission.title} {submission.selftext}")
                    if len(posts) >= MAX_POSTS:
                        break
            except Exception as e:
                print(f"Error in {subreddit}: {e}")
                continue

        if not posts:
            return "NO_DATA", 0.0

        sentiments = [TextBlob(post).sentiment.polarity for post in posts]
        avg_sentiment = sum(sentiments) / len(sentiments)
        decision = "BUY" if avg_sentiment > SENTIMENT_THRESHOLD else "HOLD"
        return decision, avg_sentiment

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return "ERROR", 0.0

def update_database():
    """Update database with sentiment analysis"""
    DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            

            cursor.execute("PRAGMA table_info(stocks)")
            columns = {col[1] for col in cursor.fetchall()}
            

            if 'sentiment' not in columns:
                cursor.execute("ALTER TABLE stocks ADD COLUMN sentiment TEXT")
            if 'sentiment_score' not in columns:
                cursor.execute("ALTER TABLE stocks ADD COLUMN sentiment_score REAL")
            if 'last_updated' not in columns:
                cursor.execute("ALTER TABLE stocks ADD COLUMN last_updated TEXT")

            cursor.execute("SELECT ticker FROM stocks")
            tickers = [row[0] for row in cursor.fetchall()]
            
            updated_count = 0
            for ticker in tickers:
                decision, score = analyze_sentiment(ticker)
                cursor.execute(
                    """UPDATE stocks 
                    SET sentiment = ?,
                        sentiment_score = ?,
                        last_updated = ?
                    WHERE ticker = ?""",
                    (decision, score, datetime.now(timezone.utc).isoformat(), ticker)
                )
                updated_count += 1

            print(f"Updated {updated_count}/{len(tickers)} stocks")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    update_database()