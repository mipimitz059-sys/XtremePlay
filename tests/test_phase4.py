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


def test_economy_gifts_and_rankings():
    user_response, user_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "econuser",
            "display_name": "Eco",
            "email": "econ@example.com",
            "password": "StrongPass123!",
        },
    )
    assert user_response.status_code == 201
    token = json.loads(user_body)["token"]

    economy_response, economy_body = run_request(
        "POST",
        "/api/v1/economy/coins",
        json_body={"amount": 250, "reason": "quest"},
        token=token,
    )
    assert economy_response.status_code == 200
    assert json.loads(economy_body)["balance"] >= 250

    gift_response, gift_body = run_request(
        "POST",
        "/api/v1/economy/gifts",
        json_body={"target_username": "econuser", "amount": 25, "message": "nice"},
        token=token,
    )
    assert gift_response.status_code == 201
    assert json.loads(gift_body)["gift"]["amount"] == 25

    ranking_response, ranking_body = run_request(
        "POST",
        "/api/v1/rankings/global",
        json_body={"score": 1200},
        token=token,
    )
    assert ranking_response.status_code == 200
    assert json.loads(ranking_body)["entry"]["score"] == 1200


def test_family_relationships_reports_and_admin():
    admin_response, admin_body = run_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": "adminx",
            "display_name": "AdminX",
            "email": "adminx@example.com",
            "password": "StrongPass123!",
            "role": "admin",
        },
    )
    assert admin_response.status_code == 201
    admin_token = json.loads(admin_body)["token"]

    family_response, family_body = run_request(
        "POST",
        "/api/v1/families",
        json_body={"name": "Nova Clan", "tag": "NV"},
        token=admin_token,
    )
    assert family_response.status_code == 201
    assert json.loads(family_body)["family"]["name"] == "Nova Clan"

    relationship_response, relationship_body = run_request(
        "POST",
        "/api/v1/relationships",
        json_body={"target_username": "adminx", "type": "bff"},
        token=admin_token,
    )
    assert relationship_response.status_code == 201
    assert json.loads(relationship_body)["relationship"]["type"] == "bff"

    report_response, report_body = run_request(
        "POST",
        "/api/v1/reports",
        json_body={"target_username": "adminx", "reason": "spam"},
        token=admin_token,
    )
    assert report_response.status_code == 201
    assert json.loads(report_body)["report"]["reason"] == "spam"

    admin_reports_response, admin_reports_body = run_request(
        "GET",
        "/api/v1/admin/reports",
        token=admin_token,
    )
    assert admin_reports_response.status_code == 200
    assert len(json.loads(admin_reports_body)["reports"]) >= 1
