import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "stocks.db"

def view_data():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.ticker, s.pe, s.decision, t.post_count, t.sentiment_score, t.last_updated 
            FROM stocks s
            LEFT JOIN sentiment t ON s.ticker = t.ticker
            """)
            
            print("\nTICKER | P/E  | BUFFETT | POSTS | SCORE | LAST UPDATED")
            print("-"*60)
            for row in cursor.fetchall():
                pe = f"{row[1]:<4.1f}" if row[1] is not None else "N/A"
                decision = row[2] if row[2] else "N/A"
                posts = f"{int(row[3]):<5}" if row[3] is not None else "0"
                score = f"{row[4]:<5.0f}" if row[4] is not None else "0"
                updated = row[5][:16] if row[5] else "N/A"
                print(f"{row[0]:<6} | {pe} | {decision:<7} | {posts} | {score} | {updated}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    view_data()