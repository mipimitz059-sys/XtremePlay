import sqlite3

DATABASE = "xtremeplay.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    # =====================================================
    # USERS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # PROFILES TABLE
    # =====================================================

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

    # =====================================================
    # FRIEND REQUESTS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,

            status TEXT DEFAULT 'pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # FRIENDS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id),

            UNIQUE(user_id, friend_id)
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


# =====================================================
# FRIEND REQUESTS
# =====================================================

def create_friend_request(sender_id: int, receiver_id: int):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO friend_requests (
            sender_id,
            receiver_id
        )
        VALUES (?, ?)
        """,
        (
            sender_id,
            receiver_id,
        ),
    )

    conn.commit()
    conn.close()


def get_friend_request(sender_id: int, receiver_id: int):
    conn = get_connection()

    request = conn.execute(
        """
        SELECT *
        FROM friend_requests
        WHERE sender_id = ?
        AND receiver_id = ?
        """,
        (
            sender_id,
            receiver_id,
        ),
    ).fetchone()

    conn.close()

    return request


def update_friend_request(request_id: int, status: str):
    conn = get_connection()

    conn.execute(
        """
        UPDATE friend_requests
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            request_id,
        ),
    )

    conn.commit()
    conn.close()


# =====================================================
# FRIENDS
# =====================================================

def add_friend(user_id: int, friend_id: int):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO friends (
            user_id,
            friend_id
        )
        VALUES (?, ?)
        """,
        (
            user_id,
            friend_id,
        ),
    )

    conn.commit()
    conn.close()


def get_friends(user_id: int):
    conn = get_connection()

    friends = conn.execute(
        """
        SELECT
            users.id,
            users.username,
            profiles.display_name,
            profiles.avatar_url

        FROM friends

        JOIN users
            ON users.id = friends.friend_id

        LEFT JOIN profiles
            ON profiles.user_id = users.id

        WHERE friends.user_id = ?
        """,
        (user_id,),
    ).fetchall()

    conn.close()

    return friends