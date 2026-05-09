import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flexeer.db")

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # جدول المستخدمين: إضافة last_daily لتتبع المكافآت اليومية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 5.0,
            invite_code TEXT UNIQUE NOT NULL,
            referred_by TEXT,
            last_daily TEXT, -- تاريخ آخر مطالبة بالمكافأة اليومية
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول العمليات: إضافة column للمستلم لتوضيح التحويلات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            type TEXT, -- (SIGNUP, REF_REWARD, TRANSFER_OUT, TRANSFER_IN, DAILY)
            details TEXT, -- تفاصيل إضافية (مثل اسم المرسل إليه)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ تم تحديث وتهيئة قاعدة البيانات بنجاح!")

if __name__ == "__main__":
    setup_database()
