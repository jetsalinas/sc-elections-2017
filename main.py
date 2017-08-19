from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/vote')
def vote_page():
    return render_template('vote.html')

@app.route('/verify')
def verify_page():
    return render_template('verify.html')

@app.route('/logout')
def logout_page():
    return render_template('logout.html')

if __name__ == "__main__":
    app.run()
