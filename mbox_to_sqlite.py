import mailbox
import sqlite3
import os
from email.header import decode_header
from email.utils import parsedate_to_datetime

mbox_path = "input.mbox"
db_path = "mail.db"

def decode_str(s):
    if not s:
        return ""
    decoded = decode_header(s)
    result = ""
    for part, enc in decoded:
        if isinstance(part, bytes):
            result += part.decode(enc or "utf-8", errors="ignore")
        else:
            result += part
    return result

def get_bodies(msg):
    text_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition"))

            if "attachment" in disp:
                continue

            try:
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                content = payload.decode(errors="ignore")

                if ctype == "text/plain" and not text_body:
                    text_body = content
                elif ctype == "text/html" and not html_body:
                    html_body = content
            except:
                continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            content = payload.decode(errors="ignore")
            text_body = content
        except:
            pass

    return text_body, html_body


print("mbox読み込み...")
mbox = mailbox.mbox(mbox_path)
total = len(mbox)

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
CREATE TABLE mails (
    id INTEGER PRIMARY KEY,
    subject TEXT,
    sender TEXT,
    date TEXT,
    timestamp INTEGER,
    body_text TEXT,
    body_html TEXT
)
""")

c.execute("""
CREATE VIRTUAL TABLE mails_fts USING fts5(
    subject,
    sender,
    body_text,
    content='mails',
    content_rowid='id'
)
""")

conn.commit()

for i, message in enumerate(mbox):

    subject = decode_str(message["subject"])
    sender = decode_str(message["from"])
    date_raw = message["date"]
    date_str = decode_str(date_raw)

    timestamp = 0
    if date_raw:
        try:
            dt = parsedate_to_datetime(date_raw)
            timestamp = int(dt.timestamp())
        except:
            pass

    body_text, body_html = get_bodies(message)

    c.execute(
        "INSERT INTO mails VALUES (?, ?, ?, ?, ?, ?, ?)",
        (i, subject, sender, date_str, timestamp, body_text, body_html)
    )

    c.execute(
        "INSERT INTO mails_fts(rowid, subject, sender, body_text) VALUES (?, ?, ?, ?)",
        (i, subject, sender, body_text)
    )

    if i % 1000 == 0:
        print(f"{i}/{total}")

conn.commit()
conn.close()
print("完了")