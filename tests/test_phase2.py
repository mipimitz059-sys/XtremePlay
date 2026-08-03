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


def test_auth_login_and_profile():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "sora",
            "display_name": "Sora",
            "email": "sora@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    login_response, login_body = run_request(
        "POST",
        "/api/v1/auth/login",
        json_body={"username": "sora", "password": "StrongPass123!"},
    )
    assert login_response.status_code == 200
    assert json.loads(login_body)["token"]
    assert json.loads(login_body)["user"]["username"] == "sora"

    me_response, me_body = run_request("GET", "/api/v1/me", token=token)
    assert me_response.status_code == 200
    assert json.loads(me_body)["user"]["username"] == "sora"


def test_social_graph_and_search():
    register_response, first_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "rhea",
            "display_name": "Rhea",
            "email": "rhea@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    second_response, second_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "milo",
            "display_name": "Milo",
            "email": "milo@example.com",
            "password": "StrongPass123!",
        },
    )
    assert second_response.status_code == 201

    token = json.loads(second_body)["token"]
    search_response, search_body = run_request("GET", "/api/v1/users/search?query=rhe", token=token)
    assert search_response.status_code == 200
    payload = json.loads(search_body)
    assert any(item["username"] == "rhea" for item in payload["users"])

    friend_request_response, _ = run_request(
        "POST",
        "/api/v1/friends/requests",
        json_body={"target_username": "rhea"},
        token=token,
    )
    assert friend_request_response.status_code == 201

    first_token = json.loads(first_body)["token"]
    accept_response, accept_body = run_request(
        "POST",
        "/api/v1/friends/requests/milo/accept",
        token=first_token,
    )
    assert accept_response.status_code == 200
    assert json.loads(accept_body)["status"] == "accepted"

    friends_response, friends_body = run_request("GET", "/api/v1/friends", token=first_token)
    assert friends_response.status_code == 200
    assert any(friend["username"] == "milo" for friend in json.loads(friends_body)["friends"])


def test_presence_and_notifications():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "niko",
            "display_name": "Niko",
            "email": "niko@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    presence_response, presence_body = run_request(
        "POST",
        "/api/v1/presence",
        json_body={"status": "online", "channel": "lobby"},
        token=token,
    )
    assert presence_response.status_code == 200
    assert json.loads(presence_body)["status"] == "online"

    notifications_response, notifications_body = run_request("GET", "/api/v1/notifications", token=token)
    assert notifications_response.status_code == 200
    assert len(json.loads(notifications_body)["notifications"]) >= 0
