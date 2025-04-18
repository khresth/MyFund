const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const port = 3000;

const DB_PATH = path.join(__dirname, '..', 'data', 'stocks.db');

app.use(cors());
app.use(express.json());

app.get('/decisions', async (req, res) => {
  try {
    const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY, (err) => {
      if (err) {
        console.error('Database connection error:', err.message);
        return res.status(500).json({ error: 'Database connection failed' });
      }
    });

    db.all(`
      SELECT s.ticker, s.decision AS buffett_decision, t.post_count
      FROM stocks s
      LEFT JOIN sentiment t ON s.ticker = t.ticker
    `, [], (err, rows) => {
      if (err) {
        console.error('Query error:', err.message);
        return res.status(500).json({ error: 'Query failed' });
      }

      const decisions = {};
      rows.forEach(row => {
        decisions[row.ticker] = {
          buffett: row.buffett_decision || 'N/A',
          sentiment: row.post_count > 50 ? 'BUY' : 'NEUTRAL'
        };
      });

      res.json(decisions);
    });

    db.close((err) => {
      if (err) {
        console.error('Database close error:', err.message);
      }
    });
  } catch (error) {
    console.error('Server error:', error.message);
    res.status(500).json({ error: 'Server error' });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});