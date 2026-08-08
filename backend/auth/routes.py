from quart import Blueprint, request, jsonify

from backend.auth.service import (
    register,
    login,
)

auth_bp = Blueprint(
    "auth",
    __name__,
)


@auth_bp.post("/register")
async def register_route():

    data = await request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Missing JSON body",
        }), 400

    username = data.get("username")
    password = data.get("password")

    result = register(
        username=username,
        password=password,
    )

    if result["success"]:
        return jsonify(result), 201

    return jsonify(result), 409


@auth_bp.post("/login")
async def login_route():

    data = await request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Missing JSON body",
        }), 400

    username = data.get("username")
    password = data.get("password")

    result = login(
        username=username,
        password=password,
    )

    if result["success"]:
        return jsonify(result)

    return jsonify(result), 401


@auth_bp.get("/health")
async def auth_health():

    return jsonify({
        "module": "auth",
        "status": "ok",
        "database": "sqlalchemy",
    })