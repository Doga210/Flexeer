import sqlite3

def setup_database():
    conn = sqlite3.connect('flexeer.db')
    cursor = conn.cursor()

    # جدول المستخدمين: لاحظ أن الرصيد الافتراضي هو 5.0 (هدية التسجيل)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 5.0,
            invite_code TEXT UNIQUE NOT NULL,
            referred_by TEXT
        )
    ''')

    # جدول العمليات: لتتبع مكافآت الإحالة (0.05) وأول تحويل (1.0)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            type TEXT, -- (SIGNUP, REF_REWARD, TRANSFER, CASHBACK)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة البيانات بنجاح مع هدية 5 GIZ افتراضية!")

if __name__ == "__main__":
    setup_database()
