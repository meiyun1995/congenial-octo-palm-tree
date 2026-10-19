"""Small SQL-injection demonstration app.

Run with:
    python app.py

The original example used unsafe SQL concatenation; both lookup endpoints now
use parameterized queries.
"""

import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        );
        INSERT INTO users (username, email) VALUES
            ('alice', 'alice@example.com'),
            ('bob', 'bob@example.com'),
            ('carol', 'carol@example.com');
        """
    )
    return connection


@app.get("/vulnerable")
def vulnerable_search():
    """Fixed lookup retained under its original route for compatibility."""
    username = request.args.get("username", "")

    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, username, email FROM users WHERE username = ?",
            (username,),
        ).fetchall()
        return jsonify({"users": [dict(row) for row in rows]})
    finally:
        connection.close()


@app.get("/safe")
def safe_search():
    """Parameterized lookup: SQLite binds input as a value, not SQL syntax."""
    username = request.args.get("username", "")
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, username, email FROM users WHERE username = ?",
            (username,),
        ).fetchall()
        return jsonify({"users": [dict(row) for row in rows]})
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=False)
