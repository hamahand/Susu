from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime

from ..models import Payout, Payment, User, Group, Membership, PaymentStatus, PayoutStatus
from ..utils import decrypt_field
from ..integrations.momo_mock import momo_api
from ..integrations.sms_mock import SMSGateway
from .audit_service import AuditService


class PayoutService:
    """Service for managing payouts."""
    
    @staticmethod
    def check_round_complete(db: Session, group_id: int, round_number: int) -> bool:
        """
        Check if all members have paid for a specific round.
        
        Args:
            db: Database session
            group_id: Group ID
            round_number: Round number to check
            
        Returns:
            True if all members have paid, False otherwise
        """
        # Get total active members
        total_members = db.query(Membership).filter(
            Membership.group_id == group_id,
            Membership.is_active == True
        ).count()
        
        # Get successful payments for this round
        successful_payments = db.query(Payment).filter(
            Payment.group_id == group_id,
            Payment.round_number == round_number,
            Payment.status == PaymentStatus.SUCCESS
        ).count()
        
        return successful_payments >= total_members
    
    @staticmethod
    def create_payout_for_round(db: Session, group_id: int, round_number: int) -> Optional[Payout]:
        """
        Create a payout for a round if all payments are complete.
        
        Args:
            db: Database session
            group_id: Group ID
            round_number: Round number
            
        Returns:
            Created payout or None if round not complete
        """
        # Check if payout already exists for this round
        existing_payout = db.query(Payout).filter(
            Payout.group_id == group_id,
            Payout.round_number == round_number
        ).first()
        
        if existing_payout:
            return existing_payout
        
        # Check if round is complete
        if not PayoutService.check_round_complete(db, group_id, round_number):
            return None
        
        # Get group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return None
        
        # Find recipient for this round (based on rotation position)
        recipient_membership = db.query(Membership).filter(
            Membership.group_id == group_id,
            Membership.rotation_position == round_number,
            Membership.is_active == True
        ).first()
        
        if not recipient_membership:
            # If no one has this position, skip
            return None
        
        # Calculate total payout amount
        total_amount = db.query(Payment).filter(
            Payment.group_id == group_id,
            Payment.round_number == round_number,
            Payment.status == PaymentStatus.SUCCESS
        ).count() * group.contribution_amount
        
        # Create payout record
        payout = Payout(
            group_id=group_id,
            round_number=round_number,
            recipient_id=recipient_membership.user_id,
            amount=total_amount,
            status=PayoutStatus.PENDING
        )
        
        db.add(payout)
        db.commit()
        db.refresh(payout)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="payout",
            entity_id=payout.id,
            action="create",
            new_value={
                "group_id": group_id,
                "round_number": round_number,
                "recipient_id": recipient_membership.user_id,
                "amount": total_amount
            }
        )
        
        return payout
    
    @staticmethod
    def approve_payout(db: Session, payout_id: int, admin_user_id: int) -> Payout:
        """
        Approve a payout (admin action).
        
        Args:
            db: Database session
            payout_id: Payout ID
            admin_user_id: Admin user approving the payout
            
        Returns:
            Updated payout
            
        Raises:
            HTTPException: If validation fails
        """
        payout = db.query(Payout).filter(Payout.id == payout_id).first()
        
        if not payout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout not found"
            )
        
        # Check if user is admin of the group
        admin_membership = db.query(Membership).filter(
            Membership.user_id == admin_user_id,
            Membership.group_id == payout.group_id,
            Membership.is_admin == True
        ).first()
        
        if not admin_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group admins can approve payouts"
            )
        
        if payout.status == PayoutStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payout already processed"
            )
        
        # Approve payout
        old_status = payout.status
        payout.status = PayoutStatus.APPROVED
        
        db.commit()
        db.refresh(payout)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="payout",
            entity_id=payout.id,
            action="approve",
            old_value={"status": old_status.value},
            new_value={"status": "approved"},
            performed_by=admin_user_id
        )
        
        # Execute payout
        return PayoutService.execute_payout(db, payout_id)
    
    @staticmethod
    def execute_payout(db: Session, payout_id: int) -> Payout:
        """
        Execute a payout by crediting the recipient's MoMo wallet.
        
        Args:
            db: Database session
            payout_id: Payout ID
            
        Returns:
            Updated payout
            
        Raises:
            HTTPException: If payout fails
        """
        payout = db.query(Payout).filter(Payout.id == payout_id).first()
        
        if not payout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout not found"
            )
        
        if payout.status == PayoutStatus.PAID:
            return payout  # Already paid
        
        # Get recipient and group
        recipient = db.query(User).filter(User.id == payout.recipient_id).first()
        group = db.query(Group).filter(Group.id == payout.group_id).first()
        
        # Check if recipient is KYC verified
        from ..config import settings
        if settings.REQUIRE_KYC_FOR_PAYMENTS and not recipient.kyc_verified:
            payout.status = PayoutStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Recipient must complete KYC verification before receiving payouts. User ID: {recipient.id}"
            )
        
        phone = decrypt_field(recipient.phone_number)
        reference = f"Payout:Group:{group.name}|Round:{payout.round_number}|Payout:{payout.id}"
        
        try:
            transaction_id = momo_api.credit_wallet(
                phone_number=phone,
                amount=payout.amount,
                reference=reference
            )
            
            # Update payout as paid
            payout.transaction_id = transaction_id
            payout.status = PayoutStatus.PAID
            payout.payout_date = datetime.utcnow()
            
            # Move group to next round
            group.current_round += 1
            
            db.commit()
            db.refresh(payout)
            
            # Send payout notification SMS
            SMSGateway.payout_notification(
                phone_number=phone,
                amount=payout.amount,
                group_name=group.name,
                transaction_id=transaction_id
            )
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payout",
                entity_id=payout.id,
                action="execute",
                old_value={"status": "approved"},
                new_value={
                    "status": "paid",
                    "transaction_id": transaction_id,
                    "amount": payout.amount
                }
            )
            
            return payout
            
        except Exception as e:
            payout.status = PayoutStatus.FAILED
            
            db.commit()
            db.refresh(payout)
            
            # Audit log
            AuditService.log(
                db=db,
                entity_type="payout",
                entity_id=payout.id,
                action="execute_failed",
                new_value={"reason": str(e)}
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payout execution failed: {str(e)}"
            )
    
    @staticmethod
    def auto_process_payouts(db: Session):
        """
        Auto-process pending payouts that are approved or in groups with auto-payout enabled.
        This is called by the scheduler.
        """
        # Get all pending or approved payouts
        payouts = db.query(Payout).filter(
            Payout.status.in_([PayoutStatus.PENDING, PayoutStatus.APPROVED])
        ).all()
        
        for payout in payouts:
            try:
                # For auto-payout, approve and execute
                if payout.status == PayoutStatus.PENDING:
                    payout.status = PayoutStatus.APPROVED
                    db.commit()
                
                PayoutService.execute_payout(db, payout.id)
                
            except Exception as e:
                print(f"Error processing payout {payout.id}: {str(e)}")
                continue
    
    @staticmethod
    def get_current_payout(db: Session, group_id: int) -> Optional[Payout]:
        """Get current round payout for a group."""
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return None
        
        return db.query(Payout).filter(
            Payout.group_id == group_id,
            Payout.round_number == group.current_round
        ).first()

