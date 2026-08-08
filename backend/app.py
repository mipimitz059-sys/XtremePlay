from quart import Quart
import quart_cors

from backend.database.db import init_db

from backend.auth.routes import auth_bp
from backend.profile.routes import profile_bp
from backend.friends.routes import friends_bp
from backend.rooms.routes import rooms_bp
from backend.chat.routes import chat_bp
from backend.websocket.routes import websocket_bp


def create_app() -> Quart:
    app = Quart(__name__)

    # =====================================================
    # CORS
    # =====================================================

    app = quart_cors.cors(
        app,
        allow_origin="*",
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=["*"],
    )

    # =====================================================
    # DATABASE
    # =====================================================

    init_db()

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/v1/auth",
    )

    # =====================================================
    # PROFILE
    # =====================================================

    app.register_blueprint(
        profile_bp,
        url_prefix="/api/v1/profile",
    )

    # =====================================================
    # FRIENDS
    # =====================================================

    app.register_blueprint(
        friends_bp,
    )

    # =====================================================
    # ROOMS
    # =====================================================

    app.register_blueprint(
        rooms_bp,
    )

    # =====================================================
    # CHAT
    # =====================================================

    app.register_blueprint(
        chat_bp,
    )

    # =====================================================
    # REAL-TIME WEBSOCKET
    # =====================================================

    app.register_blueprint(
        websocket_bp,
    )

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "XtremePlay Backend",
            "version": "1.3.0",
            "modules": {
                "auth": "enabled",
                "profile": "enabled",
                "friends": "enabled",
                "rooms": "enabled",
                "chat": "enabled",
                "websocket": "enabled",
            },
        }

    return app


# =========================================================
# APPLICATION INSTANCE
# =========================================================

app = create_app()


# =========================================================
# DEVELOPMENT SERVER
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5003,
        debug=True,
    )