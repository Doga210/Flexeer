from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os

# إضافة المسار الحالي لتمكين استيراد logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import logic

app = Flask(__name__, template_folder="../templates")
app.secret_key = "flexeer_secret_key_123"

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = logic.login_user(username, password)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect username or password", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ref_by = request.form.get('ref_by')
        if logic.register_user(username, password, ref_by):
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Username already exists or an error occurred", "error")
    return render_template('register.html', ref=request.args.get('ref', ''))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        if logic.reset_password(username, new_password):
            flash("Password reset successful! You can now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Username not found", "error")
    return render_template('forgot_password.html')

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
