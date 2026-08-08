from backend.database.db import get_connection


def send_friend_request(sender_id: int, receiver_username: str):
    conn = get_connection()

    try:
        receiver = conn.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (receiver_username,),
        ).fetchone()

        if not receiver:
            return {
                "success": False,
                "message": "User not found",
            }

        receiver_id = receiver["id"]

        if sender_id == receiver_id:
            return {
                "success": False,
                "message": "You cannot add yourself",
            }

        existing_request = conn.execute(
            """
            SELECT id
            FROM friend_requests
            WHERE sender_id = ?
              AND receiver_id = ?
              AND status = 'pending'
            """,
            (
                sender_id,
                receiver_id,
            ),
        ).fetchone()

        if existing_request:
            return {
                "success": False,
                "message": "Friend request already sent",
            }

        existing_friend = conn.execute(
            """
            SELECT id
            FROM friends
            WHERE
                (user_id = ? AND friend_id = ?)
                OR
                (user_id = ? AND friend_id = ?)
            """,
            (
                sender_id,
                receiver_id,
                receiver_id,
                sender_id,
            ),
        ).fetchone()

        if existing_friend:
            return {
                "success": False,
                "message": "Already friends",
            }

        conn.execute(
            """
            INSERT INTO friend_requests
            (
                sender_id,
                receiver_id,
                status
            )
            VALUES
            (
                ?,
                ?,
                'pending'
            )
            """,
            (
                sender_id,
                receiver_id,
            ),
        )

        conn.commit()

        return {
            "success": True,
            "message": "Friend request sent",
        }

    finally:
        conn.close()


def get_pending_requests(user_id: int):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                friend_requests.id,
                users.id AS sender_id,
                users.username,
                friend_requests.created_at
            FROM friend_requests
            JOIN users
                ON users.id = friend_requests.sender_id
            WHERE
                friend_requests.receiver_id = ?
                AND friend_requests.status = 'pending'
            ORDER BY friend_requests.created_at DESC
            """,
            (user_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def accept_friend_request(request_id: int, receiver_id: int):
    conn = get_connection()

    try:
        request = conn.execute(
            """
            SELECT
                sender_id,
                receiver_id,
                status
            FROM friend_requests
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()

        if not request:
            return {
                "success": False,
                "message": "Friend request not found",
            }

        if request["receiver_id"] != receiver_id:
            return {
                "success": False,
                "message": "Unauthorized",
            }

        if request["status"] != "pending":
            return {
                "success": False,
                "message": "Request already processed",
            }

        sender_id = request["sender_id"]

        conn.execute(
            """
            UPDATE friend_requests
            SET status='accepted'
            WHERE id=?
            """,
            (request_id,),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO friends
            (
                user_id,
                friend_id
            )
            VALUES
            (
                ?,
                ?
            )
            """,
            (
                sender_id,
                receiver_id,
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO friends
            (
                user_id,
                friend_id
            )
            VALUES
            (
                ?,
                ?
            )
            """,
            (
                receiver_id,
                sender_id,
            ),
        )

        conn.commit()

        return {
            "success": True,
            "message": "Friend request accepted",
        }

    finally:
        conn.close()


def get_friends(user_id: int):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                users.id,
                users.username
            FROM friends
            JOIN users
                ON users.id = friends.friend_id
            WHERE friends.user_id = ?
            ORDER BY users.username ASC
            """,
            (user_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()