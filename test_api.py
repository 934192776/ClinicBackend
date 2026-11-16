import pytest
import requests

# 基础 URL
BASE_URL = "http://127.0.0.1:8000/api"


# Fixture：相当于 Postman 里的环境变量，用来提前获取 Token
@pytest.fixture(scope="session")
def admin_token():
    url = f"{BASE_URL}-token-auth/"
    payload = {"username": "admin", "password": "Clinic@2026"}
    response = requests.post(url, data=payload)

    assert response.status_code == 200, "Admin login failed!"
    token = response.json().get("token")
    return token


# 测试用例 1：获取医生列表（不需要 Token）
def test_get_doctors():
    url = f"{BASE_URL}/doctors/"
    response = requests.get(url)

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # 确保返回的是个列表


# 测试用例 2：创建医生（需要 Admin Token）
def test_create_doctor(admin_token):
    url = f"{BASE_URL}/admin/create-doctor/"
    headers = {"Authorization": f"Token {admin_token}"}
    payload = {
        "username": "pytest_doctor",
        "password": "Clinic@2026",
        "specialty": "Pytest专科"
    }

    response = requests.post(url, json=payload, headers=headers)

    # 预期返回 201 Created
    assert response.status_code == 201
    # 验证返回的 JSON 里用户名对不对
    assert response.json()["message"] == "Doctor created successfully"