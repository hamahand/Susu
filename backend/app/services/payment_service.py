from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime

from ..models import Payment, User, Group, Membership, PaymentStatus, PaymentType
from ..utils import decrypt_field
from ..integrations.momo_mock import momo_api, InsufficientFundsError
from ..integrations.sms_mock import SMSGateway
from .audit_service import AuditService


class PaymentService:
    """Service for managing payments."""
    
    @staticmethod
    def process_payment(
        db: Session,
        user_id: int,
        group_id: int,
        round_number: Optional[int] = None
    ) -> Payment:
        """
        Process a payment from a user to a group.
        
        Args:
            db: Database session
            user_id: User making the payment
            group_id: Group receiving the payment
            round_number: Round number (defaults to current round)
            
        Returns:
            Payment record
            
        Raises:
            HTTPException: If validation fails
        """
        # Get user and group
        user = db.query(User).filter(User.id == user_id).first()
        group = db.query(Group).filter(Group.id == group_id).first()
        
        if not user or not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or group not found"
            )
        
        # Check membership
        membership = db.query(Membership).filter(
            Membership.user_id == user_id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this group"
            )
        
        # Use current round if not specified
        if round_number is None:
            round_number = group.current_round
        
        # Check if group is cash-only
        if group.cash_only:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is a cash-only group. Please pay cash to your group admin, who will mark your payment as received."
            )
        
        # Check if already paid for this round
        existing_payment = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.group_id == group_id,
            Payment.round_number == round_number,
            Payment.status == PaymentStatus.SUCCESS
        ).first()
        
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already made for this round"
            )
        
        # Create pending payment record
        payment = Payment(
            user_id=user_id,
            group_id=group_id,
            round_number=round_number,
            amount=group.contribution_amount,
            status=PaymentStatus.PENDING,
            retry_count=0
        )
        
        db.add(payment)
        db.flush()
        
        # Attempt MoMo debit
        phone = decrypt_field(user.phone_number)
        reference = f"Group:{group.name}|Round:{round_number}|Payment:{payment.id}"
        
        try:
            transaction_id = momo_api.debit_wallet(
                phone_number=phone,
                amount=group.contribution_amount,
                reference=reference
            )
            
            # Update payment as successful
            payment.transaction_id = transaction_id
            payment.status = PaymentStatus.SUCCESS
            payment.payment_date = datetime.utcnow()
            
            db.commit()
            db.refresh(payment)
            
            # Send confirmation SMS
            SMSGateway.payment_confirmation(
                phone_number=phone,
                amount=group.contribution_amount,
                group_name=group.name,
                transaction_id=transaction_id
            )
            
            # Create payment notifications for other group members
            from .notification_service import NotificationService
            NotificationService.create_payment_notification(
                db=db,
                group_id=group_id,
                payer_user_id=user_id,
                round_number=round_number
            )
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payment",
                entity_id=payment.id,
                action="success",
                new_value={
                    "user_id": user_id,
                    "group_id": group_id,
                    "round": round_number,
                    "amount": group.contribution_amount,
                    "transaction_id": transaction_id
                },
                performed_by=user_id
            )
            
            return payment
            
        except InsufficientFundsError as e:
            # Update payment as failed
            payment.status = PaymentStatus.FAILED
            payment.retry_count = 1
            
            db.commit()
            db.refresh(payment)
            
            # Send failure SMS
            SMSGateway.payment_failure(
                phone_number=phone,
                amount=group.contribution_amount,
                group_name=group.name,
                retry_count=1
            )
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payment",
                entity_id=payment.id,
                action="failed",
                new_value={
                    "user_id": user_id,
                    "group_id": group_id,
                    "reason": str(e),
                    "retry_count": 1
                },
                performed_by=user_id
            )
            
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment failed: {str(e)}"
            )
    
    @staticmethod
    def retry_failed_payment(db: Session, payment_id: int) -> Payment:
        """
        Retry a failed payment.
        
        Args:
            db: Database session
            payment_id: Payment ID to retry
            
        Returns:
            Updated payment record
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not in failed status"
            )
        
        if payment.retry_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum retry attempts reached"
            )
        
        # Get user and group
        user = db.query(User).filter(User.id == payment.user_id).first()
        group = db.query(Group).filter(Group.id == payment.group_id).first()
        
        phone = decrypt_field(user.phone_number)
        reference = f"Group:{group.name}|Round:{payment.round_number}|Payment:{payment.id}|Retry:{payment.retry_count + 1}"
        
        try:
            transaction_id = momo_api.debit_wallet(
                phone_number=phone,
                amount=payment.amount,
                reference=reference
            )
            
            # Update payment as successful
            payment.transaction_id = transaction_id
            payment.status = PaymentStatus.SUCCESS
            payment.payment_date = datetime.utcnow()
            
            db.commit()
            db.refresh(payment)
            
            # Send confirmation SMS
            SMSGateway.payment_confirmation(
                phone_number=phone,
                amount=payment.amount,
                group_name=group.name,
                transaction_id=transaction_id
            )
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payment",
                entity_id=payment.id,
                action="retry_success",
                old_value={"status": "failed", "retry_count": payment.retry_count},
                new_value={"status": "success", "transaction_id": transaction_id},
                performed_by=user.id
            )
            
            return payment
            
        except InsufficientFundsError as e:
            # Increment retry count
            payment.retry_count += 1
            
            db.commit()
            db.refresh(payment)
            
            # Send failure SMS
            SMSGateway.payment_failure(
                phone_number=phone,
                amount=payment.amount,
                group_name=group.name,
                retry_count=payment.retry_count
            )
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payment",
                entity_id=payment.id,
                action="retry_failed",
                new_value={"retry_count": payment.retry_count, "reason": str(e)},
                performed_by=user.id
            )
            
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment retry failed: {str(e)}"
            )
    
    @staticmethod
    def get_user_payment_history(db: Session, user_id: int) -> List[Payment]:
        """Get payment history for a user."""
        return db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_failed_payments_for_retry(db: Session) -> List[Payment]:
        """Get all failed payments that can be retried."""
        return db.query(Payment).filter(
            Payment.status == PaymentStatus.FAILED,
            Payment.retry_count < 3
        ).all()
    
    @staticmethod
    def get_unpaid_for_user(db: Session, user_id: int, group_id: int) -> Optional[Payment]:
        """
        Get or create unpaid payment for user's current round.
        
        Returns None if already paid, Payment object if unpaid.
        """
        # Get group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check membership
        membership = db.query(Membership).filter(
            Membership.user_id == user_id,
            Membership.group_id == group_id,
            Membership.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this group"
            )
        
        # Check for existing payment in current round
        payment = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.group_id == group_id,
            Payment.round_number == group.current_round
        ).first()
        
        if payment and payment.status == PaymentStatus.SUCCESS:
            return None  # Already paid
        
        # If no payment exists, create pending one
        if not payment:
            payment = Payment(
                user_id=user_id,
                group_id=group_id,
                round_number=group.current_round,
                amount=group.contribution_amount,
                status=PaymentStatus.PENDING,
                payment_type=PaymentType.MOMO if not group.cash_only else PaymentType.CASH
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
        
        return payment
    
    @staticmethod
    def mark_as_cash_paid(
        db: Session,
        payment_id: int,
        admin_user_id: int
    ) -> Payment:
        """
        Mark a payment as cash paid by admin.
        
        Args:
            db: Database session
            payment_id: Payment ID to mark as paid
            admin_user_id: User ID of admin marking it as paid
            
        Returns:
            Updated payment record
        """
        # Get payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if already paid
        if payment.status == PaymentStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already marked as paid"
            )
        
        # Get group and check admin status
        group = db.query(Group).filter(Group.id == payment.group_id).first()
        membership = db.query(Membership).filter(
            Membership.user_id == admin_user_id,
            Membership.group_id == payment.group_id,
            Membership.is_active == True
        ).first()
        
        # Check if user is group creator or admin
        if not membership or (group.creator_id != admin_user_id and not membership.is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group admins can mark payments as paid"
            )
        
        # Update payment
        payment.status = PaymentStatus.SUCCESS
        payment.payment_type = PaymentType.CASH
        payment.payment_date = datetime.utcnow()
        payment.transaction_id = f"CASH-{int(datetime.utcnow().timestamp())}-{payment_id}"
        payment.marked_paid_by = admin_user_id
        
        db.commit()
        db.refresh(payment)
        
        # Send SMS confirmation to member
        user = db.query(User).filter(User.id == payment.user_id).first()
        phone = decrypt_field(user.phone_number)
        SMSGateway.payment_confirmation(
            phone_number=phone,
            amount=payment.amount,
            group_name=group.name,
            transaction_id=payment.transaction_id
        )
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="payment",
            entity_id=payment.id,
            action="marked_cash_paid",
            new_value={
                "payment_id": payment_id,
                "marked_by": admin_user_id,
                "amount": payment.amount,
                "transaction_id": payment.transaction_id
            },
            performed_by=admin_user_id
        )
        
        return payment

