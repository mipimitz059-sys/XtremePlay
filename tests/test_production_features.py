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


def test_notifications_family_and_analytics():
    register_response, register_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "produser",
            "display_name": "Prod",
            "email": "prod@example.com",
            "password": "StrongPass123!",
        },
    )
    assert register_response.status_code == 201
    token = json.loads(register_body)["token"]

    notify_response, notify_body = run_request("POST", "/api/v1/notifications/test", json_body={"message": "hello"}, token=token)
    assert notify_response.status_code == 201
    assert json.loads(notify_body)["notification"]["message"] == "hello"

    family_response, family_body = run_request(
        "POST",
        "/api/v1/families",
        json_body={"name": "Phoenix", "tag": "PHX"},
        token=token,
    )
    assert family_response.status_code == 201
    assert json.loads(family_body)["family"]["name"] == "Phoenix"

    analytics_response, analytics_body = run_request("GET", "/api/v1/analytics", token=token)
    assert analytics_response.status_code == 200
    assert json.loads(analytics_body)["analytics"]["room_count"] >= 0
