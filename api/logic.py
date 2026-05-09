import sqlite3
import secrets
import string
import os
from datetime import datetime
from mnemonic import Mnemonic

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSG = True
except ImportError:
    HAS_PSG = False

# System Settings
SIGNUP_BONUS = 5.0
DAILY_REWARD = 0.5
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flexeer.db")
DATABASE_URL = os.environ.get('DATABASE_URL')

mnemo = Mnemonic("english")

def get_db():
    if DATABASE_URL and HAS_PSG:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn, True
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, False

def query_db(query, params=(), one=False):
    conn, is_pg = get_db()
    try:
        if is_pg:
            query = query.replace('?', '%s')
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
        cur.execute(query, params)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()

def execute_db(query, params=(), returning_id=False):
    conn, is_pg = get_db()
    try:
        if is_pg:
            query = query.replace('?', '%s')
            if returning_id:
                query += " RETURNING id"
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
        
        cur.execute(query, params)
        last_id = None
        if returning_id:
            if is_pg:
                last_id = cur.fetchone()['id']
            else:
                last_id = cur.lastrowid
        conn.commit()
        cur.close()
        return last_id
    finally:
        conn.close()

def generate_seed_phrase():
    return mnemo.generate(strength=256)

def generate_invite_code():
    chars = string.ascii_uppercase + string.digits
    return "FLX-" + ''.join(secrets.choice(chars) for _ in range(6))

def create_wallet(seed_phrase):
    if not mnemo.check(seed_phrase):
        return False
    
    invite_code = generate_invite_code()
    try:
        user_id = execute_db(
            "INSERT INTO users (seed_phrase, invite_code, balance) VALUES (?, ?, ?)",
            (seed_phrase.strip(), invite_code, SIGNUP_BONUS),
            returning_id=True
        )
        execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'SIGNUP', 'Welcome Bonus')", (user_id, SIGNUP_BONUS))
        return user_id
    except:
        return False

def login_wallet(seed_phrase):
    phrase = seed_phrase.strip()
    if not mnemo.check(phrase):
        return None
    return query_db("SELECT * FROM users WHERE seed_phrase = ?", (phrase,), one=True)

def get_user(user_id):
    return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

def get_transactions(user_id):
    return query_db("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))

def claim_daily(user_id):
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    if user['last_daily'] == today:
        return False, "Already claimed today!"
    
    execute_db("UPDATE users SET balance = balance + ?, last_daily = ? WHERE id = ?", (DAILY_REWARD, today, user_id))
    execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'DAILY', 'Daily Reward')", (user_id, DAILY_REWARD))
    return True, f"Claimed {DAILY_REWARD} GIZ!"
