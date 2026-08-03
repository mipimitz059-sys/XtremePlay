import asyncio
import json

from main import app


def run_request(method, path, *, json_body=None, token=None):
    async def _request():
        client = app.test_client()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if json_body is None:
            response = await client.open(path, method=method, headers=headers)
        else:
            response = await client.open(
                path,
                method=method,
                headers={**headers, "Content-Type": "application/json"},
                data=json.dumps(json_body),
            )
        body = await response.get_data(as_text=True)
        return response, body

    return asyncio.run(_request())


def test_health_endpoint():
    response, body = run_request("GET", "/api/v1/health")
    assert response.status_code == 200
    payload = json.loads(body)
    assert payload["service"] == "XtremePlay"
    assert payload["status"] == "ok"


def test_auth_and_profile_flow():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "nova",
            "display_name": "Nova",
            "email": "nova@example.com",
        },
    )
    assert register_response.status_code == 201
    payload = json.loads(register_body)
    assert payload["user"]["username"] == "nova"
    token = payload["token"]

    me_response, me_body = run_request("GET", "/api/v1/me", token=token)
    assert me_response.status_code == 200
    me_payload = json.loads(me_body)
    assert me_payload["user"]["display_name"] == "Nova"


def test_room_and_leaderboard_flow():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "lyra",
            "display_name": "Lyra",
            "email": "lyra@example.com",
        },
    )
    token = json.loads(register_body)["token"]

    create_room_response, create_room_body = run_request(
        "POST",
        "/api/v1/rooms",
        json_body={"name": "Sunset Arena", "theme": "casual"},
        token=token,
    )
    assert create_room_response.status_code == 201
    room_payload = json.loads(create_room_body)
    assert room_payload["room"]["name"] == "Sunset Arena"

    rooms_response, rooms_body = run_request("GET", "/api/v1/rooms", token=token)
    assert rooms_response.status_code == 200
    rooms_payload = json.loads(rooms_body)
    assert len(rooms_payload["rooms"]) >= 1

    score_response, score_body = run_request(
        "POST",
        "/api/v1/leaderboard/score",
        json_body={"score": 500},
        token=token,
    )
    assert score_response.status_code == 200
    score_payload = json.loads(score_body)
    assert score_payload["score"] == 500

    leaderboard_response, leaderboard_body = run_request("GET", "/api/v1/leaderboard", token=token)
    assert leaderboard_response.status_code == 200
    leaderboard_payload = json.loads(leaderboard_body)
    assert leaderboard_payload["entries"][0]["username"] in {"nova", "lyra"}
