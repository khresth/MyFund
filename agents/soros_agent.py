import sqlite3
from pathlib import Path

DB_PATH = Path("C:/Users/kshit/Desktop/MyFund/data/stocks.db")

def view_data():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                s.ticker, 
                s.pe AS buffett_pe, 
                s.decision AS buffett_dec, 
                t.post_count AS sent_posts, 
                t.sentiment_score AS sent_score, 
                so.decision AS soros_dec, 
                so.pe_ratio AS soros_pe, 
                so.three_month_return AS soros_ret,
                a.decision AS ackman_dec,
                a.short_ratio AS ackman_short,
                a.pe_ratio AS ackman_pe
            FROM stocks s
            LEFT JOIN sentiment t ON s.ticker = t.ticker
            LEFT JOIN soros so ON s.ticker = so.ticker
            LEFT JOIN ackman a ON s.ticker = a.ticker
            """)
            
            print("\nTICKER | BUFFETT P/E | BUFFETT DEC | SENT POSTS | SENT SCORE | SOROS DEC | SOROS P/E | SOROS RET | ACKMAN DEC | ACKMAN SHORT | ACKMAN P/E")
            print("-"*110)
            for row in cursor.fetchall():
                ticker = row[0]
                buffett_pe = f"{row[1]:<4.1f}" if row[1] is not None else "N/A"
                buffett_dec = row[2] if row[2] else "N/A"
                sent_posts = f"{int(row[3]):<5}" if row[3] is not None else "0"
                sent_score = f"{row[4]:<5.0f}" if row[4] is not None else "0"
                soros_dec = row[5] if row[5] else "N/A"
                soros_pe = f"{row[6]:<4.1f}" if row[6] is not None else "N/A"
                soros_ret = f"{row[7]:<4.1f}" if row[7] is not None else "N/A"
                ackman_dec = row[8] if row[8] else "N/A"
                ackman_short = f"{row[9]:<4.1f}" if row[9] is not None else "N/A"
                ackman_pe = f"{row[10]:<4.1f}" if row[10] is not None else "N/A"
                print(f"{ticker:<6} | {buffett_pe:<11} | {buffett_dec:<11} | {sent_posts:<10} | {sent_score:<10} | {soros_dec:<9} | {soros_pe:<9} | {soros_ret:<9} | {ackman_dec:<10} | {ackman_short:<11} | {ackman_pe}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    view_data()