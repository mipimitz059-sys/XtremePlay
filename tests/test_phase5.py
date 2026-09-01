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


def test_profile_settings_and_daily_reward_and_moderation():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "profileuser",
            "display_name": "Profile",
            "email": "profile@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    profile_response, profile_body = run_request(
        "POST",
        "/api/v1/profile/settings",
        json_body={"bio": "Builder", "location": "Mars"},
        token=token,
    )
    assert profile_response.status_code == 200
    assert json.loads(profile_body)["profile"]["bio"] == "Builder"

    reward_response, reward_body = run_request(
        "POST",
        "/api/v1/rewards/daily",
        token=token,
    )
    assert reward_response.status_code == 200
    assert json.loads(reward_body)["reward"]["coins"] >= 100

    admin_response, admin_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "modadmin",
            "display_name": "ModAdmin",
            "email": "modadmin@example.com",
            "password": "StrongPass123!",
            "role": "admin",
        },
    )
    assert admin_response.status_code == 201
    admin_token = json.loads(admin_body)["token"]

    room_response, room_body = run_request(
        "POST",
        "/api/v1/rooms",
        json_body={"name": "Mod Room", "theme": "casual"},
        token=admin_token,
    )
    assert room_response.status_code == 201
    room_id = json.loads(room_body)["room"]["id"]

    moderation_response, moderation_body = run_request(
        "POST",
        f"/api/v1/rooms/{room_id}/moderate",
        json_body={"action": "mute", "target_username": "profileuser"},
        token=admin_token,
    )
    assert moderation_response.status_code == 200
    assert json.loads(moderation_body)["action"] == "mute"
