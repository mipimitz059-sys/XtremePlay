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


def test_room_messages_and_voice_rooms():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "phase3user",
            "display_name": "Phase3",
            "email": "phase3@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    room_response, room_body = run_request(
        "POST",
        "/api/v1/rooms",
        json_body={"name": "Neon Lounge", "theme": "party"},
        token=token,
    )
    assert room_response.status_code == 201

    message_response, message_body = run_request(
        "POST",
        "/api/v1/rooms/room-1/messages",
        json_body={"text": "hello from phase 3"},
        token=token,
    )
    assert message_response.status_code == 201
    assert json.loads(message_body)["message"]["text"] == "hello from phase 3"

    voice_room_response, voice_body = run_request(
        "POST",
        "/api/v1/voice-rooms",
        json_body={"name": "Pulse Room", "topic": "music"},
        token=token,
    )
    assert voice_room_response.status_code == 201
    assert json.loads(voice_body)["voice_room"]["name"] == "Pulse Room"
