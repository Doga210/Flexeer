import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = "8776861769:AAFOTjPvo8H-Jg7lZ_OU34agHOyZxHG5a3w"
ADMIN_ID = 8267292613 
SECRET_CODE = "aa154322" # كلمتك السرية للدخول
MY_WALLET = "UQAtucDs37OAhU3gTMUEBRxm8JhbUT2To3sxe3Qkc1mgHi3C" 

bot = telebot.TeleBot(TOKEN)
users = {} 

# --- القوائم ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💰 الرصيد", "⚙️ شراء محرك", "💸 سحب / تحويل", "📊 إحصائيات")
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("👥 عدد المستخدمين", "📢 رسالة جماعية", "🔙 العودة للقائمة")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"bal": 0.0, "phone": None, "name": message.from_user.first_name}
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = types.KeyboardButton("📱 توثيق الحساب برقم الهاتف", request_contact=True)
    markup.add(btn)
    bot.send_message(message.chat.id, "🚀 أهلاً بك في نظام Flexeer!\nيرجى توثيق حسابك:", reply_markup=markup)

# --- التعامل مع الرسائل (بما فيها الكلمة السرية) ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text

    # الدخول للوحة الآدمن بالكلمة السرية
    if text == SECRET_CODE:
        if uid == ADMIN_ID:
            bot.send_message(message.chat.id, "🛠 أهلاً بك أيها المدير. تم تفعيل لوحة التحكم:", reply_markup=admin_menu())
        else:
            bot.send_message(message.chat.id, "❌ كود غير صحيح.")
        return

    if uid not in users: return

    if text == "💰 الرصيد":
        bot.send_message(message.chat.id, f"💳 رصيدك: {users[uid]['bal']} GIZ")
    
    elif text == "⚙️ شراء محرك":
        bot.send_message(message.chat.id, f"🚀 أرسل TON للمحفظة:\n`{MY_WALLET}`\nثم أرسل الصورة للإدارة.", parse_mode="Markdown")

    elif text == "👥 عدد المستخدمين" and uid == ADMIN_ID:
        bot.send_message(ADMIN_ID, f"📊 إجمالي المشتركين: {len(users)}")

    elif text == "🔙 العودة للقائمة":
        bot.send_message(message.chat.id, "العودة للقائمة الرئيسية..", reply_markup=main_menu())

@bot.message_handler(content_types=['contact'])
def contact(message):
    uid = message.from_user.id
    if message.contact:
        if users[uid]["phone"] is None:
            users[uid]["bal"] += 10.0
            users[uid]["phone"] = message.contact.phone_number
            bot.send_message(ADMIN_ID, f"🔔 مستخدم جديد: {users[uid]['phone']} (ID: `{uid}`)")
        bot.send_message(message.chat.id, "✅ تم التوثيق! رصيدك: 10 GIZ", reply_markup=main_menu())

# نظام شحن الرصيد بالأوامر (للمدير فقط)
@bot.message_handler(commands=['set'])
def set_bal(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, target_id, amount = message.text.split()
            target_id = int(target_id)
            if target_id in users:
                users[target_id]["bal"] += float(amount)
                bot.send_message(target_id, f"🎉 مبروك! تم شحن رصيدك بـ {amount} GIZ")
                bot.send_message(ADMIN_ID, "✅ تم الشحن بنجاح.")
        except:
            bot.send_message(ADMIN_ID, "⚠️ استخدم: `/set ID Amount`")

print("🚀 المحرك يعمل الآن.. جرب الكلمة السرية!")
bot.infinity_polling()
