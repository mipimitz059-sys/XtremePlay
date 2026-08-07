from quart import Quart
import quart_cors

from backend.database.db import init_db

from backend.auth.routes import auth_bp
from backend.profile.routes import profile_bp
from backend.friends.routes import friends_bp


def create_app():
    app = Quart(__name__)

    app = quart_cors.cors(
        app,
        allow_origin="*",
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Initialize database
    init_db()

    # =====================================================
    # Register Blueprints
    # =====================================================

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/v1/auth",
    )

    app.register_blueprint(
        profile_bp,
        url_prefix="/api/v1/profile",
    )

    app.register_blueprint(
        friends_bp,
    )

    # =====================================================
    # Health Check
    # =====================================================

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "XtremePlay Backend",
            "version": "1.1.0",
            "modules": {
                "auth": "enabled",
                "profile": "enabled",
                "friends": "enabled",
            },
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5003,
        debug=True,
    )