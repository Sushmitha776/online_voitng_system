from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

# Create tables
conn = get_db()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    voted INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes(
    candidate TEXT,
    count INTEGER
)
""")

# Insert candidates
candidates = ["Chandra Babu", "Pawan Kalyan", "Jagan"]
for c in candidates:
    cursor.execute("SELECT * FROM votes WHERE candidate=?", (c,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO votes VALUES (?, ?)", (c, 0))

conn.commit()
conn.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user is None:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (username, 0))
            conn.commit()

        conn.close()
        return redirect("/vote?user=" + username)

    return render_template("login.html")

@app.route("/vote", methods=["GET", "POST"])
def vote():
    user = request.args.get("user")
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT voted FROM users WHERE username=?", (user,))
    voted = cursor.fetchone()[0]

    if voted == 1:
        return redirect("/result")

    if request.method == "POST":
        candidate = request.form["candidate"]
        cursor.execute("UPDATE votes SET count = count + 1 WHERE candidate=?", (candidate,))
        cursor.execute("UPDATE users SET voted=1 WHERE username=?", (user,))
        conn.commit()
        conn.close()
        return redirect("/result")

    conn.close()
    return render_template("vote.html")

@app.route("/result")
def result():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM votes")
    results = cursor.fetchall()
    conn.close()
    return render_template("result.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)