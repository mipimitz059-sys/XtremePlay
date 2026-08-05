import sqlite3

DATABASE = "xtremeplay.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_user(username: str, password: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO users (username, password)
        VALUES (?, ?)
        """,
        (username, password),
    )

    conn.commit()
    conn.close()


def get_user(username: str):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    conn.close()

    return user