from flask import Flask, jsonify, request, render_template, session, redirect
import sqlite3
import os
import uuid
import hashlib
import openai

DATABASE = 'database.db'

def initialize_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    email = os.environ.get('WSGI_EMAIL') or 'user@example.com'
    password = os.environ.get('WSGI_PASSWORD') or hashlib.md5(os.urandom(24)).hexdigest()
    # execute SQL statement to create users table if it doesn't exist
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY NOT NULL,
                password TEXT NOT NULL
            )
        """)
    cursor.execute("""
            INSERT OR REPLACE INTO users (email, password) VALUES (?, ?)
        """, (email, password))
    print('Login email:', email)
    print('Login password:', password)
    conn.commit()

def prepare_messages(messages):
    ret = []
    for role, content in messages:
        if role == 'bot':
            role = 'user'
        ret.append({'role': role, 'content': content})
    return ret

def chat_completion(messages):
    messages = prepare_messages(messages)
    completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', messages=messages, stream=True,
            temperature=1, presence_penalty=0, frequency_penalty=0)
    for part in completion:
        choices = part["choices"]  # type: ignore
        assert len(choices) == 1
        if 'delta' not in choices[0]:
            raise RuntimeError('no delta found in {}'.format(choices))
        if 'content' in choices[0]['delta']:
            resp = choices[0]["delta"]["content"]
            yield resp

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def index():
    if 'login_email' not in session:
        return redirect('/login')
    else:
        return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    payload = request.get_json()
    email = payload['email']
    password = payload['password']

    # connect to SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # prepare and execute SQL query to check email and password
    sql = "SELECT COUNT(*) FROM users WHERE email = ? AND password = ?"
    cursor.execute(sql, (email, password))
    count = cursor.fetchone()[0]

    # if email and password are correct, set a cookie and redirect to home page
    if count == 1:
        session['login_email'] = email
        return 'OK'
    else:
        return 'wrong email or password'

answering = {}

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if 'login_email' not in session:
        return jsonify({"status": "ERROR", "message": "NOTLOGIN"})

    payload = request.get_json()
    if "sessionid" not in session:
        session["sessionid"] = uuid.uuid4()
    sessionid = session["sessionid"]

    # Here you can implement your chatbot logic
    # to generate a response to the user's message
    if sessionid not in answering:
        messages = payload["messages"]
        answering[sessionid] = iter(chat_completion(messages))
    try:
        response = next(answering[sessionid])
    except StopIteration:
        del answering[sessionid]
        return jsonify({"status": "FINISHED", "message": ""})
    else:
        return jsonify({"status": "STREAMING", "message": response})

if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
