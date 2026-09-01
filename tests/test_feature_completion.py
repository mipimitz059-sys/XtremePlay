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


def test_profile_rewards_and_messaging_flow():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "mvpuser",
            "display_name": "MVP",
            "email": "mvp@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    settings_response, settings_body = run_request(
        "POST",
        "/api/v1/profile/settings",
        json_body={"bio": "Live gaming", "location": "Berlin", "theme": "aurora"},
        token=token,
    )
    assert settings_response.status_code == 200
    assert json.loads(settings_body)["profile"]["theme"] == "aurora"

    reward_response, reward_body = run_request("POST", "/api/v1/rewards/daily", token=token)
    assert reward_response.status_code == 200
    assert json.loads(reward_body)["balance"] >= 1000

    room_response, room_body = run_request(
        "POST",
        "/api/v1/rooms",
        json_body={"name": "MVP Arena", "theme": "party"},
        token=token,
    )
    assert room_response.status_code == 201

    message_response, message_body = run_request(
        "POST",
        f"/api/v1/rooms/{json.loads(room_body)['room']['id']}/messages",
        json_body={"text": "hello"},
        token=token,
    )
    assert message_response.status_code == 201
    assert json.loads(message_body)["message"]["text"] == "hello"

    voice_response, voice_body = run_request(
        "POST",
        "/api/v1/voice-rooms",
        json_body={"name": "MVP Voice", "topic": "music"},
        token=token,
    )
    assert voice_response.status_code == 201
    assert json.loads(voice_body)["voice_room"]["name"] == "MVP Voice"

    wallet_response, wallet_body = run_request("GET", "/api/v1/wallet", token=token)
    assert wallet_response.status_code == 200
    assert json.loads(wallet_body)["wallet"]["balance"] >= 1000
