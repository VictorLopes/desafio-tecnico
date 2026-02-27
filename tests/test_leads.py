import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_create_lead_success(client):
    with patch("app.services.lead_service.fetch_birth_date") as mock_fetch:
        mock_fetch.return_value = "1990-01-01"

        payload = {
            "name": "Test User",
            "email": "test@pytest.com",
            "phone": "+5511988887777",
        }

        response = await client.post("/leads/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "Ok"
        assert data["data"]["name"] == payload["name"]
        assert data["data"]["email"] == payload["email"]
        assert data["data"]["birth_date"] == "1990-01-01"
        assert "id" in data["data"]


@pytest.mark.asyncio
async def test_create_lead_invalid_email(client):
    payload = {
        "name": "Invalid Email",
        "email": "not-an-email",
        "phone": "+5511988887777",
    }

    response = await client.post("/leads/", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "Error"
    assert (
        "email" in data["data"].lower()
        or "value is not a valid email" in data["data"].lower()
    )


@pytest.mark.asyncio
async def test_create_lead_invalid_phone(client):
    payload = {
        "name": "Invalid Phone",
        "email": "valid@email.com",
        "phone": "abc",
    }

    response = await client.post("/leads/", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "Error"
    assert "phone" in data["data"].lower()


@pytest.mark.asyncio
async def test_list_leads(client):
    with patch("app.services.lead_service.fetch_birth_date") as mock_fetch:
        mock_fetch.return_value = "1990-01-01"
        await client.post(
            "/leads/",
            json={
                "name": "User 1",
                "email": "user1@test.com",
                "phone": "+5511911111111",
            },
        )

    response = await client.get("/leads/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Ok"
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "User 1"
