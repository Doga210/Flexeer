import os
import sys

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logic

def setup_database():
    conn, is_pg = logic.get_db()
    cursor = conn.cursor()

    id_type = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            seed_phrase TEXT UNIQUE NOT NULL,
            invite_code TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            last_daily TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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
    print("Database Initialized.")

if __name__ == "__main__":
    setup_database()
