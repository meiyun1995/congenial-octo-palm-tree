# SQL injection demonstration

This is a deliberately small Flask application for learning. It originally
demonstrated SQL injection; both endpoints are now fixed and use parameterized
queries:

- `GET /vulnerable?username=alice` retains the original route name but is now safe.
- `GET /safe?username=alice` uses a parameterized query.

## Why the original implementation was unsafe

The application treats `username` as SQL source code:

```python
query = "... WHERE username = '" + username + "'"
```

An attacker can supply quotes and SQL operators that change the meaning of the
`WHERE` clause. Depending on the database account and query, this can expose,
modify, or delete data. Error messages can also reveal database details.

The fixed endpoints pass the value separately:

```python
connection.execute("... WHERE username = ?", (username,))
```

The driver escapes and binds the value, so input remains data even when it
contains quote characters or SQL-looking text. In a real application, also use
least-privilege database credentials, avoid returning SQL errors to clients,
and add validation appropriate to the business rule.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then visit `http://127.0.0.1:5000/vulnerable?username=alice` and
`http://127.0.0.1:5000/safe?username=alice`.

The database is recreated for each request so the example stays isolated and
does not persist any data.
