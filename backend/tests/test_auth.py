"""
测试认证API
"""
import pytest


def test_register_success(client):
    """测试用户注册成功"""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"


def test_register_duplicate_username(client, test_user):
    """测试重复用户名注册"""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "another@example.com",
        "password": "password123"
    })
    assert response.status_code == 400


def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client, test_user):
    """测试错误密码登录"""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """测试获取当前用户"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
