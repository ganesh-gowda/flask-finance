from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"  

def connect_db():
    return sqlite3.connect("finance.db")


def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = connect_db()
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT * FROM entries ORDER BY date DESC")
    entries = cursor.fetchall()
    
  
    cursor.execute("SELECT type, SUM(amount) FROM entries GROUP BY type")
    summary = cursor.fetchall()
    totals = {entry[0]: entry[1] for entry in summary}
    
    conn.close()
    return render_template("home.html", entries=entries, totals=totals)


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        entry_type = request.form["type"]
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entries (type, category, amount, date) VALUES (?, ?, ?, ?)",
            (entry_type, category, amount, date),
        )
        conn.commit()
        conn.close()
        
        flash(f"{entry_type.capitalize()} entry added successfully!", "success")
        return redirect(url_for("home"))

    return render_template("add_entry.html")


@app.route("/update/<int:entry_id>", methods=["GET", "POST"])
def update_entry(entry_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":
        entry_type = request.form["type"]
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        
        cursor.execute(
            "UPDATE entries SET type = ?, category = ?, amount = ?, date = ? WHERE id = ?",
            (entry_type, category, amount, date, entry_id),
        )
        conn.commit()
        conn.close()
        flash("Entry updated successfully!", "success")
        return redirect(url_for("home"))

    cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    return render_template("update_entry.html", entry=entry)


@app.route("/delete/<int:entry_id>")
def delete_entry(entry_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    flash("Entry deleted successfully!", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
