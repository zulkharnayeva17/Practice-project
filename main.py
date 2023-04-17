from flask import Flask, request, jsonify, render_template
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

DB_HOST = "127.0.0.1"
DB_NAME = "kfc"
DB_USER = "postgres"
DB_PASS = "1234"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/')
def home():
    return render_template ('home.html')

@app.route('/login/')
def login():
    return render_template ("login.html")
def post_login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'username' in request.json and 'password' in request.json:
        username = request.json['username']
        password = request.json['password']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            password_rs = account['password']

            if check_password_hash(password_rs, password):
                return jsonify(
                    message='You have successfully logged in!',
                    user_id=account['id'],
                    username=account['username']
                )
            else:
                return jsonify(error='Incorrect username/password')
        else:
            return jsonify(error='Incorrect username/password')
    else:
        return jsonify(error='Please provide both username and password')

@app.route('/register/')
def register():
    return render_template("register.html")
def post_register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'fullname' in request.json and 'username' in request.json and 'password' in request.json and 'email' in request.json:
        fullname = request.json['fullname']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']

        _hashed_password = generate_password_hash(password)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            return jsonify(error='Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify(error='Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            return jsonify(error='Username must contain only characters and numbers!')
        elif not username or not password or not email:
            return jsonify(error='Please fill out the form!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                           (fullname, username, _hashed_password, email))
            conn.commit()
            return jsonify(message='You have successfully registered!')
    else:
        return jsonify(error='Please provide all the required fields')

@app.route('/menu/')
def menu():
    return render_template('menu.html')



@app.route('/products/')
def products():
    return render_template("product.html")
def get_products():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT * FROM product")
    rows = cursor.fetchall()

    products = []
    for row in rows:
        product = {
            'name': row['name'],
            'code': row['code'],
            'price': row['price']
        }
        products.append(product)

    return jsonify(products=products)


if __name__ == "__main__":
    app.run(debug=True)

