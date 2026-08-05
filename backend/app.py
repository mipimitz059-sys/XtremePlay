from quart import Quart
import quart_cors

from backend.auth.routes import auth_bp


def create_app():
    app = Quart(__name__)
    app = quart_cors.cors(app)

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5003)