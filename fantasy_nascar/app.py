import os

from flask import Flask
from flask import render_template
from flask_login import login_required, login_user, LoginManager, logout_user, current_user

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/account')
def accounts():
    return render_template("account.html")

@app.route('/picks/<int:id>/<string:race>')
def picks(id, race):
    return render_template("picks.html")

if __name__ == "__main__":
    app.run(debug=True)