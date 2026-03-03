from flask import Flask, render_template, request, jsonify
import sqlite3
import math
from datetime import datetime

app = Flask(__name__)
DB_PATH = "mail.db"
PER_PAGE = 50


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def format_datetime(ts):
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y/%m/%d %H:%M")
    except:
        return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/mails")
def get_mails():
    page = int(request.args.get("page", 1))
    keyword = request.args.get("q", "").strip()
    date_from = request.args.get("from", "")
    date_to = request.args.get("to", "")

    offset = (page - 1) * PER_PAGE

    conn = get_db()
    c = conn.cursor()

    where_clauses = []
    params = []

    # 日付フィルタ
    if date_from:
        ts_from = int(datetime.strptime(date_from, "%Y-%m-%d").timestamp())
        where_clauses.append("mails.timestamp >= ?")
        params.append(ts_from)

    if date_to:
        ts_to = int(datetime.strptime(date_to, "%Y-%m-%d").timestamp()) + 86400
        where_clauses.append("mails.timestamp <= ?")
        params.append(ts_to)

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    if keyword:
        count_query = f"""
            SELECT COUNT(*)
            FROM mails
            JOIN mails_fts ON mails.id = mails_fts.rowid
            {where_sql}
            {"AND" if where_sql else "WHERE"} mails_fts MATCH ?
        """
        c.execute(count_query, (*params, keyword))
        total = c.fetchone()[0]

        query = f"""
            SELECT mails.id,
                   mails.subject,
                   mails.sender,
                   mails.timestamp
            FROM mails
            JOIN mails_fts ON mails.id = mails_fts.rowid
            {where_sql}
            {"AND" if where_sql else "WHERE"} mails_fts MATCH ?
            ORDER BY mails.timestamp DESC
            LIMIT ? OFFSET ?
        """
        c.execute(query, (*params, keyword, PER_PAGE, offset))

    else:
        count_query = f"SELECT COUNT(*) FROM mails {where_sql}"
        c.execute(count_query, params)
        total = c.fetchone()[0]

        query = f"""
            SELECT mails.id,
                   mails.subject,
                   mails.sender,
                   mails.timestamp
            FROM mails
            {where_sql}
            ORDER BY mails.timestamp DESC
            LIMIT ? OFFSET ?
        """
        c.execute(query, (*params, PER_PAGE, offset))

    mails = []
    for row in c.fetchall():
        mails.append({
            "id": row["id"],
            "subject": row["subject"] or "(No Subject)",
            "sender": row["sender"] or "",
            "date": format_datetime(row["timestamp"])
        })

    conn.close()

    total_pages = max(1, math.ceil(total / PER_PAGE))

    return jsonify({
        "mails": mails,
        "page": page,
        "total_pages": total_pages
    })


@app.route("/api/mail/<int:mail_id>")
def get_mail(mail_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM mails WHERE id = ?", (mail_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "subject": row["subject"] or "(No Subject)",
        "sender": row["sender"] or "",
        "date": format_datetime(row["timestamp"]),
        "body_text": row["body_text"] or "",
        "body_html": row["body_html"] or ""
    })


if __name__ == "__main__":
    app.run(debug=True)