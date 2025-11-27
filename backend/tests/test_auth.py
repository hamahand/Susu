import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "phone_number": "+233244999999",
            "name": "New User",
            "password": "newpassword123",
            "user_type": "app"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New User"
    assert data["user_type"] == "app"
    assert "id" in data


def test_register_duplicate_user(client, test_user):
    """Test registering duplicate user fails."""
    response = client.post(
        "/auth/register",
        json={
            "phone_number": "+233244123456",  # Same as test_user
            "name": "Duplicate",
            "password": "password",
            "user_type": "app"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={
            "phone_number": "+233244123456",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/auth/login",
        json={
            "phone_number": "+233244123456",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post(
        "/auth/login",
        json={
            "phone_number": "+233244000000",
            "password": "password"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_user, auth_headers):
    """Test getting current user profile."""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test User"
    assert data["user_type"] == "app"


def test_get_current_user_unauthorized(client):
    """Test getting current user without token."""
    response = client.get("/auth/me")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

