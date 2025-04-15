import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "stocks.db"

def view_data():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT ticker, pe, sentiment, sentiment_score, last_updated 
        FROM stocks
        """)
        
        print("\nTICKER | P/E  | SENTIMENT | SCORE | LAST UPDATED")
        print("-"*60)
        for row in cursor.fetchall():
            print(f"{row[0]:<6} | {row[1]:<4.1f} | {row[2]:<9} | {row[3]:<5.2f} | {row[4][:16]}")

if __name__ == "__main__":
    view_data()