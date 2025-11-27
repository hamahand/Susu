"""Tests for admin CRM endpoints and authorization."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, Group, Payment, Payout, SystemSetting, AdminRole, UserType, PaymentStatus, GroupStatus
from app.utils.auth import get_password_hash
from app.utils.encryption import encrypt_field


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_admin.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def super_admin(db_session):
    """Create a super admin user for testing."""
    admin = User(
        phone_number=encrypt_field("+233201111111"),
        name="Super Admin",
        user_type=UserType.APP,
        password_hash=get_password_hash("password123"),
        is_system_admin=True,
        admin_role=AdminRole.SUPER_ADMIN,
        kyc_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def finance_admin(db_session):
    """Create a finance admin user for testing."""
    admin = User(
        phone_number=encrypt_field("+233202222222"),
        name="Finance Admin",
        user_type=UserType.APP,
        password_hash=get_password_hash("password123"),
        is_system_admin=True,
        admin_role=AdminRole.FINANCE_ADMIN,
        kyc_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def regular_user(db_session):
    """Create a regular non-admin user for testing."""
    user = User(
        phone_number=encrypt_field("+233203333333"),
        name="Regular User",
        user_type=UserType.APP,
        password_hash=get_password_hash("password123"),
        is_system_admin=False,
        kyc_verified=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(super_admin):
    """Get authentication token for super admin."""
    response = client.post(
        "/auth/login",
        json={"phone_number": "+233201111111", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def finance_admin_token(finance_admin):
    """Get authentication token for finance admin."""
    response = client.post(
        "/auth/login",
        json={"phone_number": "+233202222222", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def regular_user_token(regular_user):
    """Get authentication token for regular user."""
    response = client.post(
        "/auth/login",
        json={"phone_number": "+233203333333", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ==================== Authentication & Authorization Tests ====================

def test_admin_login_success(super_admin):
    """Test that admin can login successfully."""
    response = client.post(
        "/auth/login",
        json={"phone_number": "+233201111111", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_admin_access_without_token():
    """Test that admin endpoints require authentication."""
    response = client.get("/admin/dashboard/stats")
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing credentials


def test_regular_user_cannot_access_admin(regular_user_token):
    """Test that regular users cannot access admin endpoints."""
    response = client.get(
        "/admin/dashboard/stats",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 403


def test_admin_can_access_dashboard(admin_token):
    """Test that admin users can access admin endpoints."""
    response = client.get(
        "/admin/dashboard/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ==================== Dashboard Tests ====================

def test_get_dashboard_stats(admin_token, db_session, regular_user):
    """Test dashboard statistics endpoint."""
    response = client.get(
        "/admin/dashboard/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "total_users" in data
    assert "total_groups" in data
    assert "total_revenue" in data
    assert data["total_users"] >= 1  # At least the regular user


def test_get_dashboard_activity(admin_token):
    """Test dashboard activity feed endpoint."""
    response = client.get(
        "/admin/dashboard/activity?limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ==================== User Management Tests ====================

def test_list_users(admin_token, regular_user):
    """Test listing all users."""
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1


def test_list_users_with_filters(admin_token, regular_user):
    """Test listing users with filters."""
    response = client.get(
        "/admin/users?user_type=app&kyc_verified=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)


def test_get_user_detail(admin_token, regular_user):
    """Test getting user details."""
    response = client.get(
        f"/admin/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == regular_user.id
    assert data["name"] == regular_user.name


def test_update_user(admin_token, regular_user):
    """Test updating user information."""
    response = client.put(
        f"/admin/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Updated Name"}
    )
    assert response.status_code == 200


def test_verify_user_kyc(admin_token, regular_user):
    """Test manually verifying user KYC."""
    response = client.post(
        f"/admin/users/{regular_user.id}/verify-kyc",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_deactivate_user(admin_token, regular_user):
    """Test deactivating a user."""
    response = client.delete(
        f"/admin/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ==================== Group Management Tests ====================

def test_list_groups(admin_token, db_session):
    """Test listing all groups."""
    # Create a test group
    from app.utils.group_code import generate_group_code
    group = Group(
        group_code=generate_group_code(db_session),
        name="Test Group",
        contribution_amount=100.0,
        num_cycles=5,
        creator_id=1,
        status=GroupStatus.ACTIVE
    )
    db_session.add(group)
    db_session.commit()
    
    response = client.get(
        "/admin/groups",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)


def test_suspend_group(admin_token, db_session):
    """Test suspending a group."""
    # Create a test group
    from app.utils.group_code import generate_group_code
    group = Group(
        group_code=generate_group_code(db_session),
        name="Test Group",
        contribution_amount=100.0,
        num_cycles=5,
        creator_id=1,
        status=GroupStatus.ACTIVE
    )
    db_session.add(group)
    db_session.commit()
    
    response = client.post(
        f"/admin/groups/{group.id}/suspend",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ==================== Payment Management Tests ====================

def test_list_payments(admin_token):
    """Test listing all payments."""
    response = client.get(
        "/admin/payments",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_payment_status(admin_token, db_session, regular_user):
    """Test updating payment status."""
    # Create a test payment
    from app.utils.group_code import generate_group_code
    group = Group(
        group_code=generate_group_code(db_session),
        name="Test Group",
        contribution_amount=100.0,
        num_cycles=5,
        creator_id=regular_user.id,
        status=GroupStatus.ACTIVE
    )
    db_session.add(group)
    db_session.commit()
    
    payment = Payment(
        user_id=regular_user.id,
        group_id=group.id,
        round_number=1,
        amount=100.0,
        status=PaymentStatus.PENDING
    )
    db_session.add(payment)
    db_session.commit()
    
    response = client.put(
        f"/admin/payments/{payment.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "success"}
    )
    assert response.status_code == 200


# ==================== System Settings Tests ====================

def test_list_settings(admin_token):
    """Test listing system settings."""
    response = client.get(
        "/admin/settings",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_setting_super_admin_only(admin_token, finance_admin_token):
    """Test that only super admin can create settings."""
    # Super admin should succeed
    response = client.post(
        "/admin/settings",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "setting_key": "test_setting",
            "setting_value": "test_value",
            "category": "test"
        }
    )
    assert response.status_code == 200
    
    # Finance admin should fail
    response = client.post(
        "/admin/settings",
        headers={"Authorization": f"Bearer {finance_admin_token}"},
        json={
            "setting_key": "test_setting_2",
            "setting_value": "test_value",
            "category": "test"
        }
    )
    assert response.status_code == 403


# ==================== Audit Log Tests ====================

def test_list_audit_logs(admin_token):
    """Test listing audit logs."""
    response = client.get(
        "/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs_with_filters(admin_token):
    """Test listing audit logs with filters."""
    response = client.get(
        "/admin/audit-logs?entity_type=user&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ==================== Admin Management Tests ====================

def test_list_admins(admin_token):
    """Test listing all admin users."""
    response = client.get(
        "/admin/admins",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    admins = response.json()
    assert isinstance(admins, list)
    assert len(admins) >= 1


def test_create_admin_super_admin_only(admin_token, finance_admin_token):
    """Test that only super admin can create new admins."""
    # Super admin should succeed
    response = client.post(
        "/admin/admins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "phone_number": "+233204444444",
            "name": "New Admin",
            "password": "password123",
            "admin_role": "support_admin"
        }
    )
    assert response.status_code == 200
    
    # Finance admin should fail
    response = client.post(
        "/admin/admins",
        headers={"Authorization": f"Bearer {finance_admin_token}"},
        json={
            "phone_number": "+233205555555",
            "name": "Another Admin",
            "password": "password123",
            "admin_role": "support_admin"
        }
    )
    assert response.status_code == 403


def test_revoke_admin_access(admin_token, finance_admin):
    """Test revoking admin access."""
    response = client.delete(
        f"/admin/admins/{finance_admin.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_cannot_revoke_own_admin_access(admin_token, super_admin):
    """Test that admin cannot revoke their own access."""
    response = client.delete(
        f"/admin/admins/{super_admin.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


# ==================== Analytics Tests ====================

def test_get_revenue_analytics(admin_token):
    """Test revenue analytics endpoint."""
    response = client.get(
        "/admin/analytics/revenue",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "payment_count" in data


def test_get_user_analytics(admin_token):
    """Test user analytics endpoint."""
    response = client.get(
        "/admin/analytics/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "user_types" in data


def test_get_group_analytics(admin_token):
    """Test group analytics endpoint."""
    response = client.get(
        "/admin/analytics/groups",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_groups" in data


# ==================== Role-Based Access Tests ====================

def test_finance_admin_can_access_payments(finance_admin_token):
    """Test that finance admin can access payment endpoints."""
    response = client.get(
        "/admin/payments",
        headers={"Authorization": f"Bearer {finance_admin_token}"}
    )
    assert response.status_code == 200


def test_finance_admin_cannot_create_admins(finance_admin_token):
    """Test that finance admin cannot create new admins."""
    response = client.post(
        "/admin/admins",
        headers={"Authorization": f"Bearer {finance_admin_token}"},
        json={
            "phone_number": "+233206666666",
            "name": "Test Admin",
            "password": "password123",
            "admin_role": "support_admin"
        }
    )
    assert response.status_code == 403


# ==================== Cleanup ====================

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    """Cleanup test database after all tests."""
    yield
    Base.metadata.drop_all(bind=engine)

