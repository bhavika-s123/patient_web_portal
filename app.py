# imports --------------------------------------------------------------------------------------------------------------------------
import os, psycopg2
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# create app --------------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)

# configure app --------------------------------------------------------------------------------------------------------------------------
app.config['SECRET_KEY'] = 'ea_portal'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

# user class --------------------------------------------------------------------------------------------------------------------------
class User(UserMixin):
    def __init__(self, id, username, firstname, lastname, password_hash):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password_hash = password_hash

# database connection --------------------------------------------------------------------------------------------------------------------------
load_dotenv()
def get_db_connection():
    conn = psycopg2.connect(
        port=5434,
        host='drhscit.org',
        database=os.environ['DB'],
        user=os.environ['DB_UN'],
        password=os.environ['DB_PW']
    )
    return conn

# user loader --------------------------------------------------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, firstname, lastname, password_hash FROM ea_users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], firstname=user[2], lastname=user[3], password_hash=user[4])
    return None

# login --------------------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, firstname, lastname, password_hash FROM ea_users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[4], password):
            user_obj = User(id=user[0], username=user[1], firstname=user[2], lastname=user[3], password_hash=user[4])
            login_user(user_obj)
            return redirect(url_for('portal'))
        else:
            flash('incorrect username or password.', 'danger')

    return render_template('login.html')

# patient portal --------------------------------------------------------------------------------------------------------------------------
@app.route('/portal')
@login_required
def portal():
    return render_template('portal.html')

# logout --------------------------------------------------------------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# run --------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)