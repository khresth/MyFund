import praw
from textblob import TextBlob
import time  

reddit = praw.Reddit(
    client_id="TA_5pp0320yi8gfpeya9gA",
    client_secret="lUbgy61OLJVg0NGw9tNTlhaL5R_T2w",
    user_agent="MyFundBot by /u/Outrageous_Soil_845"  
)

def analyze_sentiment(ticker):
    try:

        time.sleep(2)  
        
        posts = []
        for subreddit in ["investing", "stocks"]:
            for submission in reddit.subreddit(subreddit).search(ticker, limit=3):
                posts.append(f"{submission.title} {submission.selftext}")
                if len(posts) >= 5: 
                    break

        if not posts:
            return "NO_DATA"
            
        sentiments = [TextBlob(post).sentiment.polarity for post in posts]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        return "BUY" if avg_sentiment > 0.25 else "HOLD"
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {str(e)}")
        return "ERROR"

def update_database():
    DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(stocks)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'sentiment' not in columns:
        cursor.execute("ALTER TABLE stocks ADD COLUMN sentiment TEXT")

    cursor.execute("SELECT ticker FROM stocks")
    tickers = [row[0] for row in cursor.fetchall()]

    for ticker in tickers:
        sentiment = analyze_sentiment(ticker)
        cursor.execute(
            "UPDATE stocks SET sentiment = ?, last_updated = ? WHERE ticker = ?",
            (sentiment, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ticker)
        )

    conn.commit()
    conn.close()
    print("Reddit sentiment analysis complete")

if __name__ == "__main__":
    update_database()