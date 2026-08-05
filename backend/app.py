from quart import Quart
import quart_cors

from backend.auth.routes import auth_bp
from backend.profile.routes import profile_bp
from backend.database.db import init_db


def create_app():
    app = Quart(__name__)
    app = quart_cors.cors(app)

    init_db()

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/v1/auth",
    )

    app.register_blueprint(
        profile_bp,
        url_prefix="/api/v1/profile",
    )

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "XtremePlay Backend",
            "version": "1.0.0",
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5003)