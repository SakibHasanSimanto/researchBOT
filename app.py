from flask import Flask, render_template, request, session, redirect, url_for
from utils.groq_api import call_groq_model, split_thoughts
from utils.prompt_builder import build_comparison_prompt
import os
import uuid
import sqlite3

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-default-secret-key")  # Replace in env for production

DATABASE = "history.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            paper_a_title TEXT NOT NULL,
            paper_b_title TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def extract_title(paper_text):
    lines = paper_text.strip().splitlines()
    if lines and lines[0].lower().startswith("title:"):
        return lines[0][6:].strip() or "Untitled Paper"
    return "Untitled Paper"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        paper_a = request.form.get("paper_a", "")
        paper_b = request.form.get("paper_b", "")
        selected_model = request.form.get("selected_model", "")

        prompt = build_comparison_prompt(paper_a, paper_b)

        try:
            output = call_groq_model(prompt, selected_model)
            reasoning, final_result = split_thoughts(output)

            # Track session
            session_id = session.get('id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['id'] = session_id

            # Save paper titles
            paper_a_title = extract_title(paper_a)
            paper_b_title = extract_title(paper_b)

            conn = get_db_connection()
            conn.execute(
                'INSERT INTO history (session_id, paper_a_title, paper_b_title) VALUES (?, ?, ?)',
                (session_id, paper_a_title, paper_b_title)
            )
            conn.commit()
            conn.close()

            return render_template(
                "result.html",
                paper_a=paper_a,
                paper_b=paper_b,
                selected_model=selected_model,
                result=final_result,
                reasoning=reasoning
            )
        except Exception as e:
            return render_template("error.html", message=str(e))

    return render_template("index.html")


@app.route("/history")
def history():
    session_id = session.get('id')
    if not session_id:
        return render_template("history.html", records=[])

    conn = get_db_connection()
    records = conn.execute(
        'SELECT id, paper_a_title, paper_b_title, timestamp FROM history WHERE session_id = ? ORDER BY timestamp DESC',
        (session_id,)
    ).fetchall()
    conn.close()

    return render_template("history.html", records=records)


@app.route("/history/delete/<int:record_id>", methods=["POST"])
def delete_history_item(record_id):
    session_id = session.get('id')
    if not session_id:
        return redirect(url_for('history'))

    conn = get_db_connection()
    conn.execute('DELETE FROM history WHERE id = ? AND session_id = ?', (record_id, session_id))
    conn.commit()
    conn.close()

    return redirect(url_for('history'))


@app.route("/history/delete_all", methods=["POST"])
def delete_all_history():
    session_id = session.get('id')
    if not session_id:
        return redirect(url_for('history'))

    conn = get_db_connection()
    conn.execute('DELETE FROM history WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('history'))


if __name__ == "__main__":
    app.run(debug=True)
