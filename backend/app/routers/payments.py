from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User
from ..schemas import (
    PaymentTrigger, 
    PaymentResponse, 
    PaymentHistory,
    MarkPaidRequest,
    UnpaidPaymentResponse,
    AdminPaymentRequest,
    PaymentStatusResponse
)
from ..utils import get_current_user
from ..services import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/manual-trigger", response_model=PaymentResponse)
def trigger_payment(
    payment_data: PaymentTrigger,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a payment for a group (used by USSD and app).
    Requires KYC verification.
    """
    # Import settings and check KYC requirement
    from ..config import settings
    
    # Check KYC verification status
    if settings.REQUIRE_KYC_FOR_PAYMENTS and not current_user.kyc_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC verification required for payments. Please verify your account to make payments."
        )
    
    payment = PaymentService.process_payment(
        db=db,
        user_id=current_user.id,
        group_id=payment_data.group_id
    )
    return payment


@router.get("/history", response_model=List[PaymentResponse])
def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment history for the current user.
    """
    payments = PaymentService.get_user_payment_history(db, current_user.id)
    return payments


@router.post("/{payment_id}/retry", response_model=PaymentResponse)
def retry_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed payment.
    """
    payment = PaymentService.retry_failed_payment(db, payment_id)
    return payment


@router.post("/{payment_id}/mark-paid", response_model=PaymentResponse)
def mark_payment_as_paid(
    payment_id: int,
    mark_data: MarkPaidRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a payment as cash paid (admin only).
    Admin or group creator can mark a member's payment as received in cash.
    """
    payment = PaymentService.mark_as_cash_paid(
        db=db,
        payment_id=payment_id,
        admin_user_id=current_user.id
    )
    return payment


@router.post("/{payment_id}/pay-now", response_model=PaymentResponse)
def pay_now(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Member manually triggers payment for their unpaid payment.
    For cash-only groups, this will return an error directing to admin.
    For MOMO groups, this processes the payment immediately.
    """
    from ..models import Payment, Group
    
    # Get payment
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify payment belongs to current user
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pay your own payments"
        )
    
    # Get group to check if cash-only
    group = db.query(Group).filter(Group.id == payment.group_id).first()
    
    # Process payment (will check cash_only inside)
    updated_payment = PaymentService.process_payment(
        db=db,
        user_id=current_user.id,
        group_id=payment.group_id,
        round_number=payment.round_number
    )
    
    return updated_payment


@router.post("/admin/request-payment", response_model=PaymentResponse)
def admin_request_payment(
    payment_data: AdminPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin requests payment from a group member.
    Only group admin can trigger this.
    This sends a MoMo payment request to the member's phone.
    """
    from ..models import Group, Membership
    
    # Verify user is admin of the group
    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.group_id == payment_data.group_id,
        Membership.is_admin == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can request payments"
        )
    
    # Process payment for the specified user
    payment = PaymentService.process_payment(
        db=db,
        user_id=payment_data.user_id,
        group_id=payment_data.group_id,
        round_number=payment_data.round_number
    )
    
    return payment


@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
def check_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check status of a payment request.
    Returns both local payment status and MTN transaction status if available.
    """
    from ..models import Payment
    from ..integrations.mtn_momo_integration import mtn_momo_service
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Build response
    response = PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status,
        amount=payment.amount,
        transaction_id=payment.transaction_id
    )
    
    # Get MTN transaction status if it exists
    if payment.transaction_id:
        try:
            mtn_status = mtn_momo_service.get_transaction_status(payment.transaction_id)
            response.mtn_status = mtn_status.get("status")
            response.financial_transaction_id = mtn_status.get("financial_transaction_id")
        except Exception as e:
            # If MTN status check fails, just return local status
            print(f"Failed to get MTN status: {e}")
    
    return response

