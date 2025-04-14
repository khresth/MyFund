import sqlite3
from pathlib import Path

def main():
    DB_PATH = Path(__file__).parent / "stocks.db"
    
    if not DB_PATH.exists():
        print("Error: Database file not found. Run buffett_agent.py first.")
        return
    
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
        if not cursor.fetchone():
            print("Error: 'stocks' table not found")
            return
        
        cursor.execute("SELECT * FROM stocks")
        rows = cursor.fetchall()
        
        if not rows:
            print("Table is empty")
        else:
            print("TICKER | P/E | DEBT/EQ | FCF YIELD | DECISION | LAST UPDATED")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]:<6} | {row[1]:<5.1f} | {row[2]:<7.2f} | {row[3]:<9.2%} | {row[4]:<8} | {row[5]}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()