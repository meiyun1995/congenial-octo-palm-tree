"""Small SQL-injection demonstration app.

Run with:
    python app.py

This intentionally keeps /vulnerable unsafe for training purposes. Do not use
that endpoint as a pattern for production code.
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
    """Vulnerable example: request data is concatenated into SQL."""
    username = request.args.get("username", "")
    query = "SELECT id, username, email FROM users WHERE username = '" + username + "'"

    connection = get_connection()
    try:
        rows = connection.execute(query).fetchall()
        return jsonify({"users": [dict(row) for row in rows], "query": query})
    except sqlite3.Error as error:
        return jsonify({"error": str(error), "query": query}), 400
    finally:
        connection.close()


@app.get("/safe")
def safe_search():
    """Safe counterpart: SQLite binds the input as a value, not SQL syntax."""
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
