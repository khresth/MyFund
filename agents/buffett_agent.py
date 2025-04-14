import yfinance as yf
import sqlite3
from datetime import datetime
from pathlib import Path
import os

DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True) 

def evaluate_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        pe = info.get('trailingPE', float('inf'))
        debt_to_equity = info.get('debtToEquity', 999) / 100  
        free_cash_flow = info.get('freeCashflow', 0) * 4  
        market_cap = info.get('marketCap', float('inf'))
        
        fcf_yield = free_cash_flow / market_cap if market_cap else 0
        

        if pe < 30 and debt_to_equity < 0.6 and fcf_yield > 0.025:  
            return "BUY"
        return "HOLD"
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            pe REAL,
            debt_to_equity REAL,
            fcf_yield REAL,
            decision TEXT,
            last_updated TIMESTAMP
        )
        ''')
        
        stocks = ['AAPL', 'MSFT', 'TSLA', 'JNJ', 'KO', 'PG', 'WMT', 'BRK-B']
        
        for ticker in stocks:
            decision = evaluate_stock(ticker)
            stock = yf.Ticker(ticker)
            info = stock.info
            
            cursor.execute('''
            INSERT OR REPLACE INTO stocks (ticker, pe, debt_to_equity, fcf_yield, decision, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                info.get('trailingPE'),
                info.get('debtToEquity'),
                (info.get('freeCashflow', 0) / info.get('marketCap', 1)) if info.get('marketCap') else 0,
                decision,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        
        conn.commit()
        print(f"Data saved to {DB_PATH}")
        

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("Tables in database:", cursor.fetchall())
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()