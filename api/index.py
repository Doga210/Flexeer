from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add current path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logic
import init_db

app = Flask(__name__, template_folder="templates")
app.secret_key = "flexeer_secret_key_123"

# Initialize DB if on Vercel/Postgres
try:
    init_db.setup_database()
except Exception as e:
    print(f"DB Init check: {e}")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        seed_phrase = request.form.get('seed_phrase')
        user = logic.login_user(seed_phrase)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Seed Phrase", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        seed_phrase = request.form.get('seed_phrase')
        ref_by = request.form.get('ref_by') # Get from hidden field
        if logic.register_user(seed_phrase, ref_by):
            flash("Account created! You can now log in using your phrase.", "success")
            return redirect(url_for('login'))
        else:
            flash("Invalid phrase or account already exists", "error")
    
    new_phrase = logic.generate_seed_phrase()
    # Capture 'ref' from URL parameter for the hidden field
    return render_template('register.html', seed_phrase=new_phrase, ref=request.args.get('ref', ''))

@app.route('/forgot-password')
def forgot_password():
    flash("In seed phrase systems, your phrase IS your access. If you lost it, the account cannot be recovered.", "error")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = logic.get_user_by_id(session['user_id'])
    txs = logic.get_transactions(session['user_id'])
    return render_template('dashboard.html', user=user, transactions=txs)

@app.route('/daily')
def daily():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success, message = logic.daily_reward(session['user_id'])
    flash(message, "success" if success else "error")
    return redirect(url_for('dashboard'))

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receiver_username = request.form.get('receiver')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash("Invalid amount", "error")
        return redirect(url_for('dashboard'))
    
    receiver = logic.get_user_by_username(receiver_username)
    if not receiver:
        flash("Recipient not found", "error")
    elif receiver['id'] == session['user_id']:
        flash("You cannot transfer to yourself", "error")
    else:
        result = logic.send_money(session['user_id'], receiver['id'], amount)
        flash(result, "success" if "successful" in result.lower() else "error")
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
