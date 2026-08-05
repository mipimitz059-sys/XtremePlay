import sqlite3

DATABASE = "xtremeplay.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    # ------------------------
    # Users Table
    # ------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ------------------------
    # Profiles Table
    # ------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER UNIQUE NOT NULL,

            display_name TEXT,
            bio TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            cover_url TEXT DEFAULT '',

            gender TEXT DEFAULT '',
            birthday TEXT DEFAULT '',
            country TEXT DEFAULT '',

            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,

            coins INTEGER DEFAULT 0,
            diamonds INTEGER DEFAULT 0,

            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# USERS
# =====================================================

def create_user(username: str, password: str):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO users (username, password)
        VALUES (?, ?)
        """,
        (username, password),
    )

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id


def get_user(username: str):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    conn.close()

    return user


def get_user_by_id(user_id: int):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    return user


# =====================================================
# PROFILES
# =====================================================

def create_profile(user_id: int, display_name: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO profiles (user_id, display_name)
        VALUES (?, ?)
        """,
        (
            user_id,
            display_name,
        ),
    )

    conn.commit()
    conn.close()


def get_profile(user_id: int):
    conn = get_connection()

    profile = conn.execute(
        """
        SELECT *
        FROM profiles
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    return profile


def update_profile(
    user_id: int,
    display_name: str,
    bio: str,
    country: str,
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE profiles
        SET
            display_name = ?,
            bio = ?,
            country = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """,
        (
            display_name,
            bio,
            country,
            user_id,
        ),
    )

    conn.commit()
    conn.close()