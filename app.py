from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("urls.db",
    check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT,
            short_code TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    original_url = ""

    if request.method == "POST":
        original_url = request.form["url"]
        code = generate_code()

        conn = sqlite3.connect("urls.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, code)
        )
        conn.commit()
        conn.close()

        short_url = request.host_url + code

    return render_template(
        "index.html",
        short_url=short_url,
        original_url=original_url
    )

@app.route("/<code>")
def redirect_url(code):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code=?", (code,))
    data = c.fetchone()
    conn.close()

    if data:
        return redirect(data[0])
    return "URL not found"

if __name__ == "__main__":
    app.run(debug=True)
