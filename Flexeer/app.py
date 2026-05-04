from flask import Flask, render_template, request

app = Flask(__name__)

# بيانات تجريبية (سيتم استبدالها بقاعدة بيانات لاحقاً)
user_data = {
    "balance": 100.0,
    "currency": "USD"
}

@app.route('/')
def index():
    return render_template('index.html', data=user_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

