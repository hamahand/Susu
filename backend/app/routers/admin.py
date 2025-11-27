"""Admin router for system administration endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import io

from ..database import get_db
from ..models import (
    User, Group, Payment, Payout, GroupInvitation, Membership, SystemSetting,
    AdminRole, GroupStatus, PaymentStatus, PayoutStatus, InvitationStatus, AuditLog
)
from ..utils.admin_auth import get_current_admin, require_admin_role
from ..utils.encryption import decrypt_field, encrypt_field
from ..utils.auth import get_password_hash
from ..services.admin_service import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== Schemas ====================

class AdminLoginResponse(BaseModel):
    access_token: str
    admin_role: str
    user_id: int
    name: str


class DashboardStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_groups: int
    active_groups: int
    total_revenue: float
    pending_payments: int
    pending_payouts: int
    failed_payments: int
    pending_invitations: int
    kyc_verified: int
    kyc_pending: int
    new_users_30d: int


class ActivityItem(BaseModel):
    type: str
    timestamp: datetime
    description: str
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    payment_id: Optional[int] = None


class UserListItem(BaseModel):
    id: int
    name: str
    phone_number: str
    email: Optional[str]
    user_type: str
    kyc_verified: bool
    is_system_admin: bool
    admin_role: Optional[str]
    created_at: datetime


class UserDetailResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    email: Optional[str]
    user_type: str
    kyc_verified: bool
    kyc_verified_at: Optional[datetime]
    is_system_admin: bool
    admin_role: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    total_groups: int
    total_payments: float
    active_memberships: int


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    kyc_verified: Optional[bool] = None


class CreateAdminRequest(BaseModel):
    phone_number: str
    name: str
    password: str
    admin_role: str


class GroupListItem(BaseModel):
    id: int
    group_code: str
    name: str
    contribution_amount: float
    num_cycles: int
    current_round: int
    status: str
    cash_only: bool
    member_count: int
    total_contributions: float
    created_at: datetime


class GroupDetailResponse(BaseModel):
    id: int
    group_code: str
    name: str
    contribution_amount: float
    num_cycles: int
    current_round: int
    status: str
    cash_only: bool
    creator_id: int
    created_at: datetime
    members: List[dict]
    payments_summary: dict


class GroupUpdateRequest(BaseModel):
    name: Optional[str] = None
    contribution_amount: Optional[float] = None
    status: Optional[str] = None


class PaymentListItem(BaseModel):
    id: int
    transaction_id: Optional[str]
    user_id: int
    user_name: str
    group_id: int
    group_name: str
    amount: float
    status: str
    payment_type: str
    round_number: int
    payment_date: Optional[datetime]
    created_at: datetime


class PaymentUpdateRequest(BaseModel):
    status: Optional[str] = None


class PayoutListItem(BaseModel):
    id: int
    recipient_id: int
    recipient_name: str
    group_id: int
    group_name: str
    amount: float
    status: str
    payout_date: Optional[datetime]
    created_at: datetime


class SettingItem(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    category: str
    description: Optional[str]
    updated_at: Optional[datetime]


class SettingUpdateRequest(BaseModel):
    setting_value: str


class SettingCreateRequest(BaseModel):
    setting_key: str
    setting_value: str
    category: str
    description: Optional[str] = None


class AuditLogItem(BaseModel):
    id: int
    entity_type: str
    entity_id: Optional[int]
    action: str
    performed_by: Optional[int]
    timestamp: datetime
    details: Optional[str]


# ==================== Dashboard & Analytics ====================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overview statistics for admin dashboard."""
    stats = admin_service.get_dashboard_stats(db)
    return stats


@router.get("/dashboard/activity", response_model=List[ActivityItem])
def get_dashboard_activity(
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get recent system activity."""
    activity = admin_service.get_recent_activity(db, limit)
    return activity


@router.get("/analytics/revenue")
def get_revenue_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get revenue analytics with date filters."""
    return admin_service.get_revenue_analytics(db, start_date, end_date)


@router.get("/analytics/users")
def get_user_analytics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user growth and engagement metrics."""
    return admin_service.get_user_analytics(db)


@router.get("/analytics/groups")
def get_group_analytics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get group statistics and trends."""
    return admin_service.get_group_analytics(db)


@router.get("/analytics/overview")
def get_analytics_overview(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics with time-series data."""
    return {
        "stats": admin_service.get_dashboard_stats(db),
        "time_series": admin_service.get_time_series_data(db, start_date, end_date),
        "growth": admin_service.calculate_growth_metrics(db),
        "cohort_analysis": admin_service.get_cohort_analysis(db),
        "financial_summary": admin_service.get_financial_summary(db)
    }


@router.get("/analytics/financial")
def get_financial_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get financial analytics with charts data."""
    return {
        "summary": admin_service.get_financial_summary(db),
        "time_series": admin_service.get_time_series_data(db, start_date, end_date),
        "growth": admin_service.calculate_growth_metrics(db),
        "revenue_by_type": admin_service.get_revenue_analytics(db, start_date, end_date)
    }


@router.get("/analytics/payment-trends")
def get_payment_trends(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get payment success/failure rates over time."""
    time_series = admin_service.get_time_series_data(db, start_date, end_date)
    
    if time_series:
        total_successful = sum(point["successful_transactions"] for point in time_series)
        total_failed = sum(point["failed_transactions"] for point in time_series)
        total_transactions = total_successful + total_failed
        success_rate = (total_successful / total_transactions * 100) if total_transactions > 0 else 0
    else:
        total_successful = 0
        total_failed = 0
        success_rate = 0
    
    return {
        "time_series": time_series,
        "success_rate": round(success_rate, 2),
        "total_successful": total_successful,
        "total_failed": total_failed
    }


# ==================== Bulk Operations ====================

@router.post("/bulk/users/deactivate")
def bulk_deactivate_users(
    user_ids: List[int],
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Bulk deactivate users."""
    result = admin_service.execute_bulk_operation(db, "deactivate", "user", user_ids)
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=None,
        action="bulk_deactivate",
        performed_by=admin.id,
        details=f"Admin {admin.name} bulk deactivated {result['successful']} users"
    )
    db.add(audit)
    db.commit()
    
    return result


@router.post("/bulk/users/verify-kyc")
def bulk_verify_kyc(
    user_ids: List[int],
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Bulk verify user KYC."""
    result = admin_service.execute_bulk_operation(db, "verify_kyc", "user", user_ids)
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=None,
        action="bulk_verify_kyc",
        performed_by=admin.id,
        details=f"Admin {admin.name} bulk verified KYC for {result['successful']} users"
    )
    db.add(audit)
    db.commit()
    
    return result


@router.post("/bulk/payments/retry")
def bulk_retry_payments(
    payment_ids: List[int],
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retry failed payments in bulk."""
    result = admin_service.execute_bulk_operation(db, "retry", "payment", payment_ids)
    
    # Log action
    audit = AuditLog(
        entity_type="payment",
        entity_id=None,
        action="bulk_retry",
        performed_by=admin.id,
        details=f"Admin {admin.name} bulk retried {result['successful']} payments"
    )
    db.add(audit)
    db.commit()
    
    return result


@router.post("/bulk/groups/suspend")
def bulk_suspend_groups(
    group_ids: List[int],
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Suspend multiple groups."""
    result = admin_service.execute_bulk_operation(db, "suspend", "group", group_ids)
    
    # Log action
    audit = AuditLog(
        entity_type="group",
        entity_id=None,
        action="bulk_suspend",
        performed_by=admin.id,
        details=f"Admin {admin.name} bulk suspended {result['successful']} groups"
    )
    db.add(audit)
    db.commit()
    
    return result


# ==================== User Management ====================

@router.get("/users", response_model=List[UserListItem])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    user_type: Optional[str] = None,
    kyc_verified: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all users with search and filters."""
    query = db.query(User)
    
    # Apply filters
    if user_type:
        from ..models import UserType
        query = query.filter(User.user_type == UserType(user_type))
    
    if kyc_verified is not None:
        query = query.filter(User.kyc_verified == kyc_verified)
    
    if is_admin is not None:
        query = query.filter(User.is_system_admin == is_admin)
    
    # Search by name (phone search would require decrypting all)
    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))
    
    users = query.offset(skip).limit(limit).all()
    
    # Decrypt phone numbers for response
    result = []
    for user in users:
        try:
            phone = decrypt_field(user.phone_number)
        except:
            phone = "***encrypted***"
        
        result.append(UserListItem(
            id=user.id,
            name=user.name,
            phone_number=phone,
            email=user.email,
            user_type=user.user_type.value,
            kyc_verified=user.kyc_verified,
            is_system_admin=user.is_system_admin,
            admin_role=user.admin_role.value if user.admin_role else None,
            created_at=user.created_at
        ))
    
    return result


@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user_detail(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        phone = decrypt_field(user.phone_number)
    except:
        phone = "***encrypted***"
    
    # Calculate user statistics
    total_groups = db.query(Membership).filter(Membership.user_id == user_id).count()
    active_memberships = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.is_active == True
    ).count()
    
    from sqlalchemy import func
    total_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.user_id == user_id,
        Payment.status == PaymentStatus.SUCCESS
    ).scalar() or 0.0
    
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        phone_number=phone,
        email=user.email,
        user_type=user.user_type.value,
        kyc_verified=user.kyc_verified,
        kyc_verified_at=user.kyc_verified_at,
        is_system_admin=user.is_system_admin,
        admin_role=user.admin_role.value if user.admin_role else None,
        last_login=user.last_login,
        created_at=user.created_at,
        total_groups=total_groups,
        total_payments=total_payments,
        active_memberships=active_memberships
    )


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user details."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.name is not None:
        user.name = data.name
    
    if data.email is not None:
        user.email = data.email
    
    if data.kyc_verified is not None:
        user.kyc_verified = data.kyc_verified
        if data.kyc_verified:
            user.kyc_verified_at = datetime.utcnow()
            user.kyc_provider = "manual_admin"
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=user_id,
        action="update",
        performed_by=admin.id,
        details=f"Admin {admin.name} updated user {user.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "User updated successfully", "user_id": user_id}


@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Soft delete/deactivate user (mark memberships as inactive)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Deactivate all memberships
    db.query(Membership).filter(Membership.user_id == user_id).update({"is_active": False})
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=user_id,
        action="deactivate",
        performed_by=admin.id,
        details=f"Admin {admin.name} deactivated user {user.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/verify-kyc")
def verify_kyc_manually(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually verify user's KYC."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.kyc_verified = True
    user.kyc_verified_at = datetime.utcnow()
    user.kyc_provider = "manual_admin"
    
    db.add(user)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=user_id,
        action="verify_kyc",
        performed_by=admin.id,
        details=f"Admin {admin.name} manually verified KYC for {user.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "KYC verified successfully"}


@router.post("/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: int,
    new_password: str = Query(..., min_length=6),
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Admin password reset (super admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="user",
        entity_id=user_id,
        action="reset_password",
        performed_by=admin.id,
        details=f"Admin {admin.name} reset password for {user.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.get("/users/{user_id}/activity")
def get_user_activity(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user's activity log."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's groups
    memberships = db.query(Membership).filter(Membership.user_id == user_id).all()
    groups = [m.group for m in memberships]
    
    # Get user's payments
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).limit(20).all()
    
    # Get user's payouts
    payouts = db.query(Payout).filter(Payout.recipient_id == user_id).order_by(Payout.created_at.desc()).limit(20).all()
    
    return {
        "user_id": user_id,
        "groups": [{"id": g.id, "name": g.name, "status": g.status.value} for g in groups],
        "recent_payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "status": p.status.value,
                "date": p.payment_date
            } for p in payments
        ],
        "recent_payouts": [
            {
                "id": p.id,
                "amount": p.amount,
                "status": p.status.value,
                "date": p.payout_date
            } for p in payouts
        ]
    }


# ==================== Group Management ====================

@router.get("/groups", response_model=List[GroupListItem])
def list_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    status: Optional[str] = None,
    cash_only: Optional[bool] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all groups with filters."""
    from sqlalchemy import func
    
    query = db.query(Group)
    
    # Apply filters
    if status:
        query = query.filter(Group.status == GroupStatus(status))
    
    if cash_only is not None:
        query = query.filter(Group.cash_only == cash_only)
    
    if search:
        query = query.filter(Group.name.ilike(f"%{search}%"))
    
    groups = query.offset(skip).limit(limit).all()
    
    result = []
    for group in groups:
        member_count = db.query(Membership).filter(
            Membership.group_id == group.id,
            Membership.is_active == True
        ).count()
        
        total_contributions = db.query(func.sum(Payment.amount)).filter(
            Payment.group_id == group.id,
            Payment.status == PaymentStatus.SUCCESS
        ).scalar() or 0.0
        
        result.append(GroupListItem(
            id=group.id,
            group_code=group.group_code,
            name=group.name,
            contribution_amount=group.contribution_amount,
            num_cycles=group.num_cycles,
            current_round=group.current_round,
            status=group.status.value,
            cash_only=group.cash_only,
            member_count=member_count,
            total_contributions=total_contributions,
            created_at=group.created_at
        ))
    
    return result


@router.get("/groups/{group_id}", response_model=GroupDetailResponse)
def get_group_detail(
    group_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed group information."""
    from sqlalchemy import func
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get members
    memberships = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.is_active == True
    ).all()
    
    members = []
    for m in memberships:
        try:
            phone = decrypt_field(m.user.phone_number)
        except:
            phone = "***encrypted***"
        
        members.append({
            "user_id": m.user.id,
            "name": m.user.name,
            "phone": phone,
            "rotation_position": m.rotation_position,
            "is_admin": m.is_admin
        })
    
    # Payment summary
    total_paid = db.query(func.sum(Payment.amount)).filter(
        Payment.group_id == group_id,
        Payment.status == PaymentStatus.SUCCESS
    ).scalar() or 0.0
    
    pending_payments = db.query(Payment).filter(
        Payment.group_id == group_id,
        Payment.status == PaymentStatus.PENDING
    ).count()
    
    return GroupDetailResponse(
        id=group.id,
        group_code=group.group_code,
        name=group.name,
        contribution_amount=group.contribution_amount,
        num_cycles=group.num_cycles,
        current_round=group.current_round,
        status=group.status.value,
        cash_only=group.cash_only,
        creator_id=group.creator_id,
        created_at=group.created_at,
        members=members,
        payments_summary={
            "total_paid": total_paid,
            "pending_payments": pending_payments
        }
    )


@router.put("/groups/{group_id}")
def update_group(
    group_id: int,
    data: GroupUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update group settings."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if data.name is not None:
        group.name = data.name
    
    if data.contribution_amount is not None:
        group.contribution_amount = data.contribution_amount
    
    if data.status is not None:
        group.status = GroupStatus(data.status)
    
    db.add(group)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="group",
        entity_id=group_id,
        action="update",
        performed_by=admin.id,
        details=f"Admin {admin.name} updated group {group.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Group updated successfully"}


@router.post("/groups/{group_id}/suspend")
def suspend_group(
    group_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Suspend a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.status = GroupStatus.SUSPENDED
    db.add(group)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="group",
        entity_id=group_id,
        action="suspend",
        performed_by=admin.id,
        details=f"Admin {admin.name} suspended group {group.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Group suspended successfully"}


@router.post("/groups/{group_id}/reactivate")
def reactivate_group(
    group_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reactivate a suspended group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.status = GroupStatus.ACTIVE
    db.add(group)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="group",
        entity_id=group_id,
        action="reactivate",
        performed_by=admin.id,
        details=f"Admin {admin.name} reactivated group {group.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Group reactivated successfully"}


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a group (super admin only)."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Log action before deletion
    audit = AuditLog(
        entity_type="group",
        entity_id=group_id,
        action="delete",
        performed_by=admin.id,
        details=f"Admin {admin.name} deleted group {group.name}"
    )
    db.add(audit)
    db.commit()
    
    # Delete group (will cascade to memberships, payments, etc. if configured)
    db.delete(group)
    db.commit()
    
    return {"message": "Group deleted successfully"}


@router.post("/groups/{group_id}/remove-member")
def remove_member_from_group(
    group_id: int,
    user_id: int = Query(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Remove a member from a group."""
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    membership.is_active = False
    db.add(membership)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="membership",
        entity_id=membership.id,
        action="remove_member",
        performed_by=admin.id,
        details=f"Admin {admin.name} removed user {user_id} from group {group_id}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Member removed successfully"}


# ==================== Payment & Transaction Management ====================

@router.get("/payments", response_model=List[PaymentListItem])
def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    payment_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all payments with filters."""
    query = db.query(Payment).join(User, Payment.user_id == User.id).join(Group, Payment.group_id == Group.id)
    
    # Apply filters
    if status:
        query = query.filter(Payment.status == PaymentStatus(status))
    
    if payment_type:
        from ..models import PaymentType
        query = query.filter(Payment.payment_type == PaymentType(payment_type))
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for payment in payments:
        result.append(PaymentListItem(
            id=payment.id,
            transaction_id=payment.transaction_id,
            user_id=payment.user_id,
            user_name=payment.user.name,
            group_id=payment.group_id,
            group_name=payment.group.name,
            amount=payment.amount,
            status=payment.status.value,
            payment_type=payment.payment_type.value,
            round_number=payment.round_number,
            payment_date=payment.payment_date,
            created_at=payment.created_at
        ))
    
    return result


@router.get("/payments/{payment_id}")
def get_payment_detail(
    payment_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get payment details."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    try:
        user_phone = decrypt_field(payment.user.phone_number)
    except:
        user_phone = "***encrypted***"
    
    return {
        "id": payment.id,
        "transaction_id": payment.transaction_id,
        "user": {
            "id": payment.user.id,
            "name": payment.user.name,
            "phone": user_phone
        },
        "group": {
            "id": payment.group.id,
            "name": payment.group.name,
            "code": payment.group.group_code
        },
        "amount": payment.amount,
        "status": payment.status.value,
        "payment_type": payment.payment_type.value,
        "round_number": payment.round_number,
        "payment_date": payment.payment_date,
        "retry_count": payment.retry_count,
        "created_at": payment.created_at
    }


@router.put("/payments/{payment_id}")
def update_payment(
    payment_id: int,
    data: PaymentUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update payment status."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    old_status = payment.status
    
    if data.status:
        payment.status = PaymentStatus(data.status)
        if data.status == "success" and not payment.payment_date:
            payment.payment_date = datetime.utcnow()
    
    db.add(payment)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="payment",
        entity_id=payment_id,
        action="update_status",
        performed_by=admin.id,
        old_value={"status": old_status.value},
        new_value={"status": payment.status.value},
        details=f"Admin {admin.name} updated payment status from {old_status.value} to {payment.status.value}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Payment updated successfully"}


@router.get("/payments/pending")
def get_pending_payments(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending payments requiring attention."""
    payments = db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).order_by(Payment.created_at).all()
    
    result = []
    for payment in payments:
        result.append({
            "id": payment.id,
            "user_name": payment.user.name,
            "group_name": payment.group.name,
            "amount": payment.amount,
            "round_number": payment.round_number,
            "created_at": payment.created_at
        })
    
    return result


@router.get("/payments/failed")
def get_failed_payments(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get failed payments for review."""
    payments = db.query(Payment).filter(Payment.status == PaymentStatus.FAILED).order_by(Payment.created_at.desc()).all()
    
    result = []
    for payment in payments:
        result.append({
            "id": payment.id,
            "user_name": payment.user.name,
            "group_name": payment.group.name,
            "amount": payment.amount,
            "retry_count": payment.retry_count,
            "created_at": payment.created_at
        })
    
    return result


# ==================== Payout Management ====================

@router.get("/payouts", response_model=List[PayoutListItem])
def list_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all payouts."""
    query = db.query(Payout).join(User, Payout.recipient_id == User.id).join(Group, Payout.group_id == Group.id)
    
    if status:
        query = query.filter(Payout.status == PayoutStatus(status))
    
    payouts = query.order_by(Payout.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for payout in payouts:
        result.append(PayoutListItem(
            id=payout.id,
            recipient_id=payout.recipient_id,
            recipient_name=payout.recipient.name,
            group_id=payout.group_id,
            group_name=payout.group.name,
            amount=payout.amount,
            status=payout.status.value,
            payout_date=payout.payout_date,
            created_at=payout.created_at
        ))
    
    return result


@router.get("/payouts/{payout_id}")
def get_payout_detail(
    payout_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get payout details."""
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    try:
        recipient_phone = decrypt_field(payout.recipient.phone_number)
    except:
        recipient_phone = "***encrypted***"
    
    return {
        "id": payout.id,
        "recipient": {
            "id": payout.recipient.id,
            "name": payout.recipient.name,
            "phone": recipient_phone
        },
        "group": {
            "id": payout.group.id,
            "name": payout.group.name,
            "code": payout.group.group_code
        },
        "amount": payout.amount,
        "status": payout.status.value,
        "round_number": payout.round_number,
        "payout_date": payout.payout_date,
        "created_at": payout.created_at
    }


@router.post("/payouts/{payout_id}/approve")
def approve_payout(
    payout_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a payout."""
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    # Here you would integrate with actual payout processing
    payout.status = PayoutStatus.SUCCESS
    payout.payout_date = datetime.utcnow()
    db.add(payout)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="payout",
        entity_id=payout_id,
        action="approve",
        performed_by=admin.id,
        details=f"Admin {admin.name} approved payout of {payout.amount} to {payout.recipient.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Payout approved successfully"}


@router.post("/payouts/{payout_id}/reject")
def reject_payout(
    payout_id: int,
    reason: str = Query(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a payout."""
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = PayoutStatus.FAILED
    db.add(payout)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="payout",
        entity_id=payout_id,
        action="reject",
        performed_by=admin.id,
        details=f"Admin {admin.name} rejected payout: {reason}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Payout rejected"}


# ==================== Invitation Management ====================

@router.get("/invitations")
def list_invitations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all invitations."""
    query = db.query(GroupInvitation)
    
    if status:
        query = query.filter(GroupInvitation.status == InvitationStatus(status))
    
    invitations = query.order_by(GroupInvitation.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for inv in invitations:
        try:
            phone = decrypt_field(inv.phone_number)
        except:
            phone = "***encrypted***"
        
        result.append({
            "id": inv.id,
            "group_id": inv.group_id,
            "group_name": inv.group.name,
            "phone_number": phone,
            "invited_by": inv.inviter.name,
            "status": inv.status.value,
            "created_at": inv.created_at,
            "accepted_at": inv.accepted_at
        })
    
    return result


@router.post("/invitations/{invitation_id}/expire")
def expire_invitation(
    invitation_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually expire an invitation."""
    invitation = db.query(GroupInvitation).filter(GroupInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    invitation.status = InvitationStatus.EXPIRED
    db.add(invitation)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="invitation",
        entity_id=invitation_id,
        action="expire",
        performed_by=admin.id,
        details=f"Admin {admin.name} expired invitation {invitation_id}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Invitation expired"}


@router.delete("/invitations/{invitation_id}")
def delete_invitation(
    invitation_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Remove an invitation."""
    invitation = db.query(GroupInvitation).filter(GroupInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    db.delete(invitation)
    db.commit()
    
    return {"message": "Invitation deleted"}


# ==================== System Settings ====================

@router.get("/settings", response_model=List[SettingItem])
def list_settings(
    category: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all system settings."""
    query = db.query(SystemSetting)
    
    if category:
        query = query.filter(SystemSetting.category == category)
    
    settings = query.all()
    
    return [SettingItem(
        id=s.id,
        setting_key=s.setting_key,
        setting_value=s.setting_value,
        category=s.category,
        description=s.description,
        updated_at=s.updated_at
    ) for s in settings]


@router.get("/settings/{category}")
def get_settings_by_category(
    category: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get settings by category."""
    settings = db.query(SystemSetting).filter(SystemSetting.category == category).all()
    return [SettingItem(
        id=s.id,
        setting_key=s.setting_key,
        setting_value=s.setting_value,
        category=s.category,
        description=s.description,
        updated_at=s.updated_at
    ) for s in settings]


@router.put("/settings/{setting_key}")
def update_setting(
    setting_key: str,
    data: SettingUpdateRequest,
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Update a system setting (super admin only)."""
    setting = db.query(SystemSetting).filter(SystemSetting.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    old_value = setting.setting_value
    setting.setting_value = data.setting_value
    setting.updated_by = admin.id
    setting.updated_at = datetime.utcnow()
    
    db.add(setting)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="system_setting",
        entity_id=setting.id,
        action="update",
        performed_by=admin.id,
        old_value={"value": old_value},
        new_value={"value": data.setting_value},
        details=f"Admin {admin.name} updated setting {setting_key}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Setting updated successfully"}


@router.post("/settings")
def create_setting(
    data: SettingCreateRequest,
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new system setting (super admin only)."""
    # Check if already exists
    existing = db.query(SystemSetting).filter(SystemSetting.setting_key == data.setting_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting already exists")
    
    setting = SystemSetting(
        setting_key=data.setting_key,
        setting_value=data.setting_value,
        category=data.category,
        description=data.description,
        updated_by=admin.id
    )
    
    db.add(setting)
    db.commit()
    db.refresh(setting)
    
    # Log action
    audit = AuditLog(
        entity_type="system_setting",
        entity_id=setting.id,
        action="create",
        performed_by=admin.id,
        details=f"Admin {admin.name} created setting {data.setting_key}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Setting created successfully", "id": setting.id}


# ==================== Audit Logs ====================

@router.get("/audit-logs", response_model=List[AuditLogItem])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    performed_by: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get searchable audit log with filters."""
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if performed_by:
        query = query.filter(AuditLog.performed_by == performed_by)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [AuditLogItem(
        id=log.id,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        action=log.action,
        performed_by=log.performed_by,
        timestamp=log.timestamp,
        details=log.details
    ) for log in logs]


@router.get("/audit-logs/entity/{entity_type}/{entity_id}")
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific entity."""
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.timestamp.desc()).all()
    
    return [AuditLogItem(
        id=log.id,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        action=log.action,
        performed_by=log.performed_by,
        timestamp=log.timestamp,
        details=log.details
    ) for log in logs]


# ==================== Admin Management ====================

@router.get("/admins")
def list_admins(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all admin users."""
    admins = db.query(User).filter(User.is_system_admin == True).all()
    
    result = []
    for a in admins:
        try:
            phone = decrypt_field(a.phone_number)
        except:
            phone = "***encrypted***"
        
        result.append({
            "id": a.id,
            "name": a.name,
            "phone": phone,
            "admin_role": a.admin_role.value if a.admin_role else None,
            "last_login": a.last_login,
            "created_at": a.created_at
        })
    
    return result


@router.post("/admins")
def create_admin(
    data: CreateAdminRequest,
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new admin user (super admin only)."""
    # Check if user already exists
    all_users = db.query(User).all()
    for u in all_users:
        try:
            if decrypt_field(u.phone_number) == data.phone_number:
                raise HTTPException(status_code=400, detail="User already exists")
        except:
            continue
    
    # Create admin user
    from ..models import UserType
    encrypted_phone = encrypt_field(data.phone_number)
    
    new_admin = User(
        phone_number=encrypted_phone,
        name=data.name,
        user_type=UserType.APP,
        password_hash=get_password_hash(data.password),
        is_system_admin=True,
        admin_role=AdminRole(data.admin_role),
        momo_account_id=encrypted_phone
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    # Log action
    audit = AuditLog(
        entity_type="admin",
        entity_id=new_admin.id,
        action="create",
        performed_by=admin.id,
        details=f"Super Admin {admin.name} created new admin {data.name} with role {data.admin_role}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Admin created successfully", "admin_id": new_admin.id}


@router.put("/admins/{admin_id}")
def update_admin_role(
    admin_id: int,
    new_role: str = Query(...),
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Update admin role (super admin only)."""
    target_admin = db.query(User).filter(User.id == admin_id).first()
    if not target_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    if not target_admin.is_system_admin:
        raise HTTPException(status_code=400, detail="User is not an admin")
    
    old_role = target_admin.admin_role
    target_admin.admin_role = AdminRole(new_role)
    
    db.add(target_admin)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="admin",
        entity_id=admin_id,
        action="update_role",
        performed_by=admin.id,
        old_value={"role": old_role.value if old_role else None},
        new_value={"role": new_role},
        details=f"Super Admin {admin.name} updated admin {target_admin.name} role"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Admin role updated successfully"}


@router.delete("/admins/{admin_id}")
def revoke_admin_access(
    admin_id: int,
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Revoke admin access (super admin only)."""
    if admin_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot revoke your own admin access")
    
    target_admin = db.query(User).filter(User.id == admin_id).first()
    if not target_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    target_admin.is_system_admin = False
    target_admin.admin_role = None
    
    db.add(target_admin)
    db.commit()
    
    # Log action
    audit = AuditLog(
        entity_type="admin",
        entity_id=admin_id,
        action="revoke",
        performed_by=admin.id,
        details=f"Super Admin {admin.name} revoked admin access from {target_admin.name}"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Admin access revoked successfully"}


# ==================== Database Management ====================

@router.get("/database/tables")
def get_database_tables(
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """List all database tables with row counts."""
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    
    result = []
    for table_name in tables:
        row_count = db.execute(func.count(1).select_from(inspector.get_table(table_name))).scalar()
        result.append({
            "name": table_name,
            "row_count": row_count
        })
    
    return {"tables": result}


@router.post("/database/query")
def execute_database_query(
    query: str = Query(...),
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Execute read-only SQL query (super admin only)."""
    # Security: Only allow SELECT queries
    query_lower = query.strip().lower()
    if not query_lower.startswith('select'):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    try:
        result = db.execute(query)
        rows = []
        for row in result:
            rows.append(dict(row._mapping))
        
        return {
            "rows": rows,
            "count": len(rows)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/database/stats")
def get_database_stats(
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Get database statistics."""
    from ..config import settings
    
    # Get database connection info
    return {
        "database_url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "hidden",
        "database_name": "sususave",
        "redis_url": settings.REDIS_URL,
        "uptime": "N/A"  # Would need to track this
    }


@router.get("/database/migrations")
def get_database_migrations(
    admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Get database migration status."""
    try:
        # Check Alembic version
        from alembic import config as alembic_config
        from alembic.runtime.migration import MigrationContext
        
        mc = MigrationContext.configure(db.connection())
        current_rev = mc.get_current_revision()
        
        return {
            "current_revision": current_rev,
            "status": "up to date"
        }
    except Exception as e:
        return {
            "current_revision": "unknown",
            "status": f"error: {str(e)}"
        }


# ==================== System Configuration ====================

@router.get("/system/health")
def get_system_health(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Comprehensive system health check."""
    health_status = {
        "database": "healthy",
        "redis": "healthy",
        "api": "healthy"
    }
    
    try:
        # Check database
        db.execute("SELECT 1")
    except:
        health_status["database"] = "unhealthy"
    
    # Check Redis (if configured)
    from ..config import settings
    if settings.USE_REDIS:
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
        except:
            health_status["redis"] = "unhealthy"
    
    return health_status


@router.get("/system/services")
def get_services_status(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get status of external services."""
    from ..config import settings
    
    return {
        "mtn_services": {
            "ussd": settings.ENABLE_MTN_USSD,
            "sms": settings.ENABLE_MTN_SMS,
            "momo": settings.ENABLE_MTN_MOMO
        },
        "africas_talking": {
            "username": settings.AT_USERNAME,
            "environment": settings.AT_ENVIRONMENT
        },
        "sms_gateway": {
            "enabled": settings.ENABLE_REAL_SMS,
            "provider": "mock" if not settings.ENABLE_REAL_SMS else "real"
        }
    }


# ==================== Export Functions ====================

@router.get("/export/users")
def export_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export users to CSV."""
    csv_data = admin_service.export_users_csv(db)
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


@router.get("/export/payments")
def export_payments(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export payments to CSV."""
    csv_data = admin_service.export_payments_csv(db, start_date, end_date)
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payments_export.csv"}
    )

