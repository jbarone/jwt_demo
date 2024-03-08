import uuid
import sqlite3
import string
import random

with sqlite3.connect("db.sqlite3") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS keys (id TEXT, key TEXT);")
    for _ in range(10):
        cursor.execute(
            "INSERT INTO keys (id, key) VALUES (?, ?);",
            (
                str(uuid.uuid4()),
                "".join(random.choice(string.ascii_letters) for _ in range(100)),
            ),
        )
    conn.commit()
    cursor.close()
