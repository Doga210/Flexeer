from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sys

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logic
import init_db

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "flexeer_ultra_secure_key")

# Auto-init DB
try:
    init_db.setup_database()
except Exception as e:
    print(f"DB Error: {e}")

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        seed_phrase = request.form.get('seed_phrase')
        user_id = logic.create_wallet(seed_phrase)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        else:
            flash("Failed to create wallet. Phrase might already exist.", "error")
            return redirect(url_for('home'))
            
    phrase = logic.generate_seed_phrase()
    return render_template('create.html', phrase=phrase)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        seed_phrase = request.form.get('seed_phrase')
        user = logic.login_wallet(seed_phrase)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Seed Phrase. Please check and try again.", "error")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = logic.get_user(session['user_id'])
    txs = logic.get_transactions(session['user_id'])
    return render_template('dashboard.html', user=user, transactions=txs)

@app.route('/daily')
def daily():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success, message = logic.claim_daily(session['user_id'])
    flash(message, "success" if success else "error")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


import telebot
import os

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "8776861769:AAFOTjPvo8H-Jg7lZ_OU34agHOyZxHG5a3w")
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🏦 أهلاً بك في Flexeer Wallet!")
