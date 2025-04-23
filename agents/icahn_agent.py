import yfinance as yf
import sqlite3
from datetime import datetime
from pathlib import Path

import sqlite3
from pathlib import Path

DB_PATH = Path("C:/Users/kshit/Desktop/MyFund/data/stocks.db")
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS icahn")
conn.commit()
conn.close()
print("Dropped icahn table")

DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
TICKERS = ['AAPL', 'MSFT', 'TSLA', 'JNJ', 'KO', 'PG', 'WMT', 'BRK-B']

def get_icahn_signal(ticker):
    """
    Generate trading signal based on Carl Icahn's activist strategy.
    Criteria:
    - P/E ratio < 15 (undervalued)
    - Short interest > 5% (potential for short squeeze or mispricing)
    - Return on Equity (ROE) > 10% (strong fundamentals)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        

        pe_ratio = info.get('trailingPE', float('inf'))
        short_ratio = info.get('shortPercentOfFloat', 0) * 100  
        roe = info.get('returnOnEquity', 0) * 100  
        

        if pe_ratio < 15 and short_ratio > 5 and roe > 10:
            return 'BUY'
        return 'HOLD'
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return 'HOLD'

def update_icahn_table():
    """
    Update the icahn table in the database with signals and metrics for each ticker.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS icahn (
            ticker TEXT PRIMARY KEY,
            decision TEXT,
            pe_ratio REAL,
            short_ratio REAL,
            roe REAL,
            last_updated TEXT
        )
    ''')
    

    for ticker in TICKERS:
        decision = get_icahn_signal(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info
        

        pe_ratio = info.get('trailingPE', float('inf'))
        short_ratio = info.get('shortPercentOfFloat', 0) * 100
        roe = info.get('returnOnEquity', 0) * 100
        last_updated = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        

        cursor.execute('''
            INSERT OR REPLACE INTO icahn (ticker, decision, pe_ratio, short_ratio, roe, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, decision, pe_ratio, short_ratio, roe, last_updated))
    
    conn.commit()
    conn.close()
    print(f"Updated {len(TICKERS)} stocks in icahn table")

if __name__ == '__main__':
    update_icahn_table()