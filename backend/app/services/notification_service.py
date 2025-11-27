from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..models import Notification, Membership, Payment, PaymentStatus


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_payment_notification(
        db: Session, 
        group_id: int, 
        payer_user_id: int, 
        round_number: int
    ) -> int:
        """
        Create payment notifications for all group members except the payer.
        
        Args:
            db: Database session
            group_id: Group ID
            payer_user_id: User ID of the person who made the payment
            round_number: Round number for the payment
            
        Returns:
            Number of notifications created
        """
        # Get all active group members except the payer
        memberships = db.query(Membership).filter(
            Membership.group_id == group_id,
            Membership.is_active == True,
            Membership.user_id != payer_user_id
        ).all()
        
        # Count total members and paid members for the message
        total_members = db.query(Membership).filter(
            Membership.group_id == group_id,
            Membership.is_active == True
        ).count()
        
        paid_members = db.query(Payment).filter(
            Payment.group_id == group_id,
            Payment.round_number == round_number,
            Payment.status == PaymentStatus.SUCCESS
        ).count()
        
        # Create notification for each member
        notifications_created = 0
        for membership in memberships:
            notification = Notification(
                user_id=membership.user_id,
                group_id=group_id,
                notification_type="payment_made",
                message=f"A member just paid! {paid_members} of {total_members} members have paid for Round {round_number}",
                is_read=False,
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            notifications_created += 1
        
        db.commit()
        return notifications_created
    
    @staticmethod
    def get_user_notifications(
        db: Session, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            
        Returns:
            List of notifications
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read.
        
        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            True if notification was marked as read, False otherwise
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        updated_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        return updated_count
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
