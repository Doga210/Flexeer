import os

# Try to import logic to use its connection
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logic

def setup_database():
    conn, is_pg = logic.get_db()
    cursor = conn.cursor()

    # WIPE DATA (Optional: Remove after use)
    print("⚠️ Wiping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS transactions CASCADE")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")

    # User table
    id_type = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            seed_phrase TEXT UNIQUE NOT NULL,
            username TEXT,
            password TEXT,
            balance REAL DEFAULT 5.0,
            invite_code TEXT UNIQUE NOT NULL,
            referred_by TEXT,
            last_daily TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Transactions table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS transactions (
            id {id_type},
            user_id INTEGER,
            amount REAL,
            type TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized successfully ({'PostgreSQL' if is_pg else 'SQLite'})!")

if __name__ == "__main__":
    setup_database()
