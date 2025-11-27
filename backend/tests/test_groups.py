import pytest
from fastapi import status


def test_create_group(client, auth_headers):
    """Test creating a new group."""
    response = client.post(
        "/groups",
        headers=auth_headers,
        json={
            "name": "Test Savings Group",
            "contribution_amount": 100.0,
            "num_cycles": 12
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Savings Group"
    assert data["contribution_amount"] == 100.0
    assert data["num_cycles"] == 12
    assert data["current_round"] == 1
    assert data["status"] == "active"
    assert "group_code" in data
    assert data["group_code"].startswith("SUSU")


def test_create_group_unauthorized(client):
    """Test creating group without authentication."""
    response = client.post(
        "/groups",
        json={
            "name": "Test Group",
            "contribution_amount": 50.0,
            "num_cycles": 10
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_my_groups(client, auth_headers):
    """Test getting user's groups."""
    # First create a group
    client.post(
        "/groups",
        headers=auth_headers,
        json={
            "name": "My Test Group",
            "contribution_amount": 50.0,
            "num_cycles": 6
        }
    )
    
    # Get user's groups
    response = client.get("/groups/my-groups", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "My Test Group"


def test_join_group(client, auth_headers, db_session, test_user):
    """Test joining a group via group code."""
    # Create a group first
    create_response = client.post(
        "/groups",
        headers=auth_headers,
        json={
            "name": "Join Test Group",
            "contribution_amount": 75.0,
            "num_cycles": 8
        }
    )
    group_code = create_response.json()["group_code"]
    
    # Create another user to join
    from app.models import User, UserType
    from app.utils import encrypt_field, get_password_hash
    
    new_user = User(
        phone_number=encrypt_field("+233244888888"),
        name="Joiner",
        user_type=UserType.APP,
        momo_account_id=encrypt_field("+233244888888"),
        password_hash=get_password_hash("password123")
    )
    db_session.add(new_user)
    db_session.commit()
    
    # Login as new user
    login_response = client.post(
        "/auth/login",
        json={"phone_number": "+233244888888", "password": "password123"}
    )
    new_token = login_response.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}
    
    # Join the group
    join_response = client.post(
        "/groups/join",
        headers=new_headers,
        json={"group_code": group_code}
    )
    
    assert join_response.status_code == status.HTTP_200_OK
    data = join_response.json()
    assert data["message"] == "Successfully joined group"
    assert data["rotation_position"] == 2  # Second member


def test_join_nonexistent_group(client, auth_headers):
    """Test joining a group that doesn't exist."""
    response = client.post(
        "/groups/join",
        headers=auth_headers,
        json={"group_code": "SUSUXXXX"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_group_details(client, auth_headers):
    """Test getting group details."""
    # Create group
    create_response = client.post(
        "/groups",
        headers=auth_headers,
        json={
            "name": "Detail Test Group",
            "contribution_amount": 60.0,
            "num_cycles": 10
        }
    )
    group_id = create_response.json()["id"]
    
    # Get details
    response = client.get(f"/groups/{group_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == group_id
    assert data["name"] == "Detail Test Group"


def test_get_group_dashboard(client, auth_headers):
    """Test getting group dashboard data."""
    # Create group
    create_response = client.post(
        "/groups",
        headers=auth_headers,
        json={
            "name": "Dashboard Test",
            "contribution_amount": 50.0,
            "num_cycles": 5
        }
    )
    group_id = create_response.json()["id"]
    
    # Get dashboard
    response = client.get(f"/groups/{group_id}/dashboard", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "group" in data
    assert "members" in data
    assert "total_collected_current_round" in data
    assert len(data["members"]) == 1  # Creator is the only member
    assert data["members"][0]["is_admin"] is True

