import yfinance as yf
import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data" / "stocks.db"
TICKERS = ['AAPL', 'MSFT', 'TSLA', 'JNJ', 'KO', 'PG', 'WMT', 'BRK-B']

def get_soros_signal(ticker):
    """
    Generate trading signal based on George Soros's momentum strategy.
    Criteria:
    - 3-month return > 10% (strong price momentum)
    - P/E ratio < 25 (reasonable valuation)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo")
        

        if len(hist) < 2:
            return 'HOLD'
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        three_month_return = ((end_price - start_price) / start_price) * 100
        

        pe_ratio = info.get('trailingPE', float('inf'))
        

        if three_month_return > 10 and pe_ratio < 25:
            return 'BUY'
        return 'HOLD'
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return 'HOLD'

def update_soros_table():
    """
    Update the soros table in the database with signals and metrics for each ticker.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soros (
            ticker TEXT PRIMARY KEY,
            decision TEXT,
            pe_ratio REAL,
            three_month_return REAL,
            last_updated TEXT
        )
    ''')
    

    for ticker in TICKERS:
        decision = get_soros_signal(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo")
        

        three_month_return = 0
        if len(hist) >= 2:
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            three_month_return = ((end_price - start_price) / start_price) * 100
        

        pe_ratio = info.get('trailingPE', float('inf'))
        last_updated = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        cursor.execute('''
            INSERT OR REPLACE INTO soros (ticker, decision, pe_ratio, three_month_return, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, decision, pe_ratio, three_month_return, last_updated))
    
    conn.commit()
    conn.close()
    print(f"Updated {len(TICKERS)} stocks in soros table")

def view_data():
    """
    Display aggregated data from all agents in a formatted table.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
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
                    a.pe_ratio AS ackman_pe,
                    i.decision AS icahn_dec,
                    i.pe_ratio AS icahn_pe,
                    i.short_ratio AS icahn_short,
                    i.roe AS icahn_roe
                FROM stocks s
                LEFT JOIN sentiment t ON s.ticker = t.ticker
                LEFT JOIN soros so ON s.ticker = so.ticker
                LEFT JOIN ackman a ON s.ticker = a.ticker
                LEFT JOIN icahn i ON s.ticker = i.ticker
            """)
            
            print("\nTICKER | BUFFETT P/E | BUFFETT DEC | SENT POSTS | SENT SCORE | SOROS DEC | SOROS P/E | SOROS RET | ACKMAN DEC | ACKMAN SHORT | ACKMAN P/E | ICAHN DEC | ICAHN P/E | ICAHN SHORT | ICAHN ROE")
            print("-"*140)
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
                icahn_dec = row[11] if row[11] else "N/A"
                icahn_pe = f"{row[12]:<4.1f}" if row[12] is not None else "N/A"
                icahn_short = f"{row[13]:<4.1f}" if row[13] is not None else "N/A"
                icahn_roe = f"{row[14]:<4.1f}" if row[14] is not None else "N/A"
                print(f"{ticker:<6} | {buffett_pe:<11} | {buffett_dec:<11} | {sent_posts:<10} | {sent_score:<10} | {soros_dec:<9} | {soros_pe:<9} | {soros_ret:<9} | {ackman_dec:<10} | {ackman_short:<11} | {ackman_pe:<10} | {icahn_dec:<9} | {icahn_pe:<9} | {icahn_short:<11} | {icahn_roe}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    update_soros_table()
    view_data()