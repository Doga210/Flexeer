import sqlite3
import secrets
import string

# إعدادات النظام التي استقرينا عليها
SIGNUP_BONUS = 5.0
REF_REWARD = 0.05
FIRST_TX_BONUS = 1.0
MIN_TRANSFER = 10.0

def get_db():
    conn = sqlite3.connect('flexeer.db')
    conn.row_factory = sqlite3.Row
    return conn

# توليد كود إحالة فريد
def generate_ref_code():
    chars = string.ascii_uppercase + string.digits
    return "FLX-" + ''.join(secrets.choice(chars) for _ in range(6))

# وظيفة التسجيل مع مكافأة الإحالة
def register_user(username, password, ref_by=None):
    db = get_db()
    my_code = generate_ref_code()
    try:
        # إضافة المستخدم الجديد مع رصيد 5 GIZ
        db.execute("INSERT INTO users (username, password, balance, invite_code, referred_by) VALUES (?, ?, ?, ?, ?)",
                   (username, password, SIGNUP_BONUS, my_code, ref_by))
        
        # إذا سجل عبر كود إحالة، نمنح الصديق 0.05 GIZ
        if ref_by:
            db.execute("UPDATE users SET balance = balance + ? WHERE invite_code = ?", (REF_REWARD, ref_by))
            
        db.commit()
        return True
    except:
        return False
    finally:
        db.close()

# وظيفة التحويل مع المكافآت والقيود
def send_money(sender_id, receiver_id, amount):
    if amount < MIN_TRANSFER:
        return "الحد الأدنى للتحويل هو 10 GIZ"
    
    db = get_db()
    sender = db.execute("SELECT balance FROM users WHERE id = ?", (sender_id,)).fetchone()
    
    if sender['balance'] < amount:
        return "رصيدك غير كافٍ"

    # التحقق هل هذا أول تحويل له في التاريخ؟
    tx_count = db.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ? AND type = 'TRANSFER'", (sender_id,)).fetchone()[0]
    bonus = FIRST_TX_BONUS if tx_count == 0 else 0.0

    # تنفيذ العملية
    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender_id))
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount + bonus, receiver_id))
    
    # تسجيل العملية في السجل
    db.execute("INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, 'TRANSFER')", (sender_id, -amount))
    
    db.commit()
    db.close()
    return f"تم التحويل! المكافأة الممنوحة: {bonus} GIZ"
