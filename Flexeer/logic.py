import sqlite3
import secrets
import string
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# System Settings
SIGNUP_BONUS = 5.0
REF_REWARD = 0.05
FIRST_TX_BONUS = 1.0
MIN_TRANSFER = 10.0
DAILY_REWARD = 0.1

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flexeer.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_ref_code():
    chars = string.ascii_uppercase + string.digits
    return "FLX-" + ''.join(secrets.choice(chars) for _ in range(6))

def register_user(username, password, ref_by=None):
    db = get_db()
    my_code = generate_ref_code()
    hashed_password = generate_password_hash(password)
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password, balance, invite_code, referred_by) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, SIGNUP_BONUS, my_code, ref_by)
        )
        user_id = cursor.lastrowid
        
        # Register signup bonus
        db.execute("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'SIGNUP', 'Signup Reward')", (user_id, SIGNUP_BONUS))
        
        # Referral reward
        if ref_by:
            referrer = db.execute("SELECT id FROM users WHERE invite_code = ?", (ref_by,)).fetchone()
            if referrer:
                db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (REF_REWARD, referrer['id']))
                db.execute("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'REF_REWARD', ?)", 
                           (referrer['id'], REF_REWARD, f"New referral: {username}"))
            
        db.commit()
        return True
    except:
        return False
    finally:
        db.close()

def login_user(username, password):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user

def get_user_by_username(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user

def get_transactions(user_id):
    db = get_db()
    txs = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
    db.close()
    return txs

def reset_password(username, new_password):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if user:
        hashed_password = generate_password_hash(new_password)
        db.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user['id']))
        db.commit()
        db.close()
        return True
    db.close()
    return False

def daily_reward(user_id):
    db = get_db()
    user = db.execute("SELECT last_daily FROM users WHERE id = ?", (user_id,)).fetchone()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user['last_daily'] == today:
        db.close()
        return False, "You have already claimed your daily reward today!"
    
    db.execute("UPDATE users SET balance = balance + ?, last_daily = ? WHERE id = ?", (DAILY_REWARD, today, user_id))
    db.execute("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'DAILY', 'Daily Reward')", (user_id, DAILY_REWARD))
    db.commit()
    db.close()
    return True, f"Successfully received {DAILY_REWARD} GIZ!"

def send_money(sender_id, receiver_id, amount):
    if amount < MIN_TRANSFER:
        return f"Minimum transfer amount is {MIN_TRANSFER} GIZ"
    
    db = get_db()
    sender = db.execute("SELECT balance, username FROM users WHERE id = ?", (sender_id,)).fetchone()
    receiver = db.execute("SELECT username FROM users WHERE id = ?", (receiver_id,)).fetchone()
    
    if sender['balance'] < amount:
        db.close()
        return "Insufficient balance"

    # First transaction bonus
    tx_count = db.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ? AND type = 'TRANSFER_OUT'", (sender_id,)).fetchone()[0]
    bonus = FIRST_TX_BONUS if tx_count == 0 else 0.0

    # Execute transaction
    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender_id))
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount + bonus, receiver_id))
    
    # Record transactions
    db.execute("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'TRANSFER_OUT', ?)", 
               (sender_id, -amount, f"Sent to {receiver['username']}"))
    db.execute("INSERT INTO transactions (user_id, amount, type, details) VALUES (?, ?, 'TRANSFER_IN', ?)", 
               (receiver_id, amount + bonus, f"Received from {sender['username']} {f'+ bonus {bonus}' if bonus > 0 else ''}"))
    
    db.commit()
    db.close()
    return f"Transfer successful! Bonus awarded: {bonus} GIZ"
