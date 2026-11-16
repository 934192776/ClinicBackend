import pytest
import requests
import random

BASE_URL = "http://127.0.0.1:8000/api"


@pytest.fixture(scope="session")
def admin_token():
    url = f"{BASE_URL}-token-auth/"
    payload = {"username": "admin", "password": "Clinic@2026"}
    response = requests.post(url, data=payload)
    assert response.status_code == 200, "Admin login failed!"
    return response.json().get("token")


def test_get_doctors():
    url = f"{BASE_URL}/doctors/"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_doctor(admin_token):
    url = f"{BASE_URL}/admin/create-doctor/"
    headers = {"Authorization": f"Token {admin_token}"}


    random_num = random.randint(1000, 9999)

    payload = {
        "username": f"pytest_doctor_{random_num}",
        "password": "Clinic@2026",
        "specialty": "Pytest专科"
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 201