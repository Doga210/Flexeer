import sqlite3
import secrets
import string
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSG = True
except ImportError:
    HAS_PSG = False

# System Settings
SIGNUP_BONUS = 5.0
REF_REWARD = 0.05
FIRST_TX_BONUS = 1.0
MIN_TRANSFER = 10.0
DAILY_REWARD = 0.1

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flexeer.db")
DATABASE_URL = os.environ.get('DATABASE_URL')

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
    if is_pg:
        query = query.replace('?', '%s')
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cur = conn.cursor()
    
    cur.execute(query, params)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, params=(), returning_id=False):
    conn, is_pg = get_db()
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
    conn.close()
    return last_id

def generate_ref_code():
    chars = string.ascii_uppercase + string.digits
    return "FLX-" + ''.join(secrets.choice(chars) for _ in range(6))

def register_user(username, password, ref_by=None):
    my_code = generate_ref_code()
    hashed_password = generate_password_hash(password)
    try:
        user_id = execute_db(
            "INSERT INTO users (username, password, balance, invite_code, referred_by) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, SIGNUP_BONUS, my_code, ref_by),
            returning_id=True
        )
        
        # Register signup bonus
        execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'SIGNUP', 'Signup Reward')", (user_id, SIGNUP_BONUS))
        
        # Referral reward
        if ref_by:
            referrer = query_db("SELECT id FROM users WHERE invite_code = ?", (ref_by,), one=True)
            if referrer:
                execute_db("UPDATE users SET balance = balance + ? WHERE id = ?", (REF_REWARD, referrer['id']))
                execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'REF_REWARD', ?)", 
                           (referrer['id'], REF_REWARD, f"New referral: {username}"))
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def login_user(username, password):
    user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_by_id(user_id):
    return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

def get_user_by_username(username):
    return query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)

def get_transactions(user_id):
    return query_db("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))

def reset_password(username, new_password):
    user = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)
    if user:
        hashed_password = generate_password_hash(new_password)
        execute_db("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user['id']))
        return True
    return False

def daily_reward(user_id):
    user = query_db("SELECT last_daily FROM users WHERE id = ?", (user_id,), one=True)
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user['last_daily'] == today:
        return False, "You have already claimed your daily reward today!"
    
    execute_db("UPDATE users SET balance = balance + ?, last_daily = ? WHERE id = ?", (DAILY_REWARD, today, user_id))
    execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'DAILY', 'Daily Reward')", (user_id, DAILY_REWARD))
    return True, f"Successfully received {DAILY_REWARD} GIZ!"

def send_money(sender_id, receiver_id, amount):
    if amount < MIN_TRANSFER:
        return f"Minimum transfer amount is {MIN_TRANSFER} GIZ"
    
    sender = query_db("SELECT balance, username FROM users WHERE id = ?", (sender_id,), one=True)
    receiver = query_db("SELECT username FROM users WHERE id = ?", (receiver_id,), one=True)
    
    if sender['balance'] < amount:
        return "Insufficient balance"

    # First transaction bonus
    tx_count_res = query_db("SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND type = 'TRANSFER_OUT'", (sender_id,), one=True)
    tx_count = tx_count_res['count']
    bonus = FIRST_TX_BONUS if tx_count == 0 else 0.0

    # Execute transaction
    execute_db("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender_id))
    execute_db("UPDATE users SET balance = balance + ? WHERE id = ?", (amount + bonus, receiver_id))
    
    # Record transactions
    execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'TRANSFER_OUT', ?)", 
               (sender_id, -amount, f"Sent to {receiver['username']}"))
    execute_db("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'TRANSFER_IN', ?)", 
               (receiver_id, amount + bonus, f"Received from {sender['username']} {f'+ bonus {bonus}' if bonus > 0 else ''}"))
    
    return f"Transfer successful! Bonus awarded: {bonus} GIZ"
