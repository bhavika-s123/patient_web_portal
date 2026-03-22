# imports
import os
import psycopg2
from flask import Flask
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# configure app
app = Flask(__name__)
bcrypt = Bcrypt(app)

# load env vars
load_dotenv()

# connect to your existing database
conn = psycopg2.connect(
    port=5434,
    host='drhscit.org',
    database=os.environ['DB'],
    user=os.environ['DB_UN'],
    password=os.environ['DB_PW']
)
cur = conn.cursor()

# create the ea_users table if it doesn't exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS ea_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        firstname VARCHAR(100),
        lastname VARCHAR(100),
        password_hash VARCHAR(255) NOT NULL,
        isreadonly BOOLEAN DEFAULT FALSE,
        isadmin BOOLEAN DEFAULT FALSE
    );
''')
conn.commit()

# test patient account data
username = 'patient'
firstname = 'patient'
lastname = 'example'
plain_password = '123'
is_admin = False
is_readonly = False

# delete existing user with the same username
cur.execute('DELETE FROM ea_users WHERE username = %s;', (username,))

# hash password
hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

# insert new user
cur.execute(
    'INSERT INTO ea_users (username, firstname, lastname, password_hash, isreadonly, isadmin) VALUES (%s, %s, %s, %s, %s, %s)',
    (username, firstname, lastname, hashed_password, is_readonly, is_admin)
)
conn.commit()

# verify insert and password
cur.execute('SELECT * FROM ea_users WHERE username = %s;', (username,))
user_data = cur.fetchone()
if user_data and bcrypt.check_password_hash(user_data[4], plain_password):
    print('EUREKA! Password hashes match!')
else:
    print('Wah wah')

# close connections
cur.close()
conn.close()