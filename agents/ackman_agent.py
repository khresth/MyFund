import yfinance as yf
import sqlite3
from datetime import datetime
import os


TICKERS = ['AAPL', 'MSFT', 'TSLA', 'JNJ', 'KO', 'PG', 'WMT', 'BRK-B']


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'stocks.db')

def get_ackman_signal(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        short_ratio = info.get('shortPercentOfFloat', 0) * 100  
        pe_ratio = info.get('trailingPE', float('inf'))
        

        if pe_ratio < 20 and short_ratio > 10:
            return 'BUY'
        return 'HOLD'
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return 'HOLD'

def update_ackman_table():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ackman (
            ticker TEXT PRIMARY KEY,
            decision TEXT,
            short_ratio REAL,
            pe_ratio REAL,
            last_updated TEXT
        )
    ''')
    
    for ticker in TICKERS:
        decision = get_ackman_signal(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info
        short_ratio = info.get('shortPercentOfFloat', 0) * 100
        pe_ratio = info.get('trailingPE', float('inf'))
        last_updated = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        cursor.execute('''
            INSERT OR REPLACE INTO ackman (ticker, decision, short_ratio, pe_ratio, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, decision, short_ratio, pe_ratio, last_updated))
    
    conn.commit()
    conn.close()
    print(f"Updated {len(TICKERS)} stocks in ackman table")

if __name__ == '__main__':
    update_ackman_table()