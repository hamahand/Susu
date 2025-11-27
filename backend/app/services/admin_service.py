"""Admin service for dashboard statistics, analytics, and administrative operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import csv
import io

from ..models import (
    User, Group, Payment, Payout, GroupInvitation, Membership,
    PaymentStatus, PayoutStatus, GroupStatus, InvitationStatus, UserType
)
from ..utils.encryption import decrypt_field


class AdminService:
    """Service for admin-related operations."""
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Get overview statistics for admin dashboard.
        
        Returns:
            Dictionary with key metrics like total users, groups, revenue, etc.
        """
        total_users = db.query(User).count()
        active_users = db.query(User).join(Membership).filter(Membership.is_active == True).distinct().count()
        
        total_groups = db.query(Group).count()
        active_groups = db.query(Group).filter(Group.status == GroupStatus.ACTIVE).count()
        
        # Calculate total revenue from successful payments
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.SUCCESS
        ).scalar() or 0.0
        
        # Pending payments needing attention
        pending_payments = db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).count()
        
        # Pending payouts needing approval
        pending_payouts = db.query(Payout).filter(Payout.status == PayoutStatus.PENDING).count()
        
        # Failed payments needing review
        failed_payments = db.query(Payment).filter(Payment.status == PaymentStatus.FAILED).count()
        
        # Pending invitations
        pending_invitations = db.query(GroupInvitation).filter(
            GroupInvitation.status == InvitationStatus.PENDING
        ).count()
        
        # KYC verification stats
        kyc_verified = db.query(User).filter(User.kyc_verified == True).count()
        kyc_pending = total_users - kyc_verified
        
        # User growth (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_30d = db.query(User).filter(User.created_at >= thirty_days_ago).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_groups": total_groups,
            "active_groups": active_groups,
            "total_revenue": round(total_revenue, 2),
            "pending_payments": pending_payments,
            "pending_payouts": pending_payouts,
            "failed_payments": failed_payments,
            "pending_invitations": pending_invitations,
            "kyc_verified": kyc_verified,
            "kyc_pending": kyc_pending,
            "new_users_30d": new_users_30d,
        }
    
    @staticmethod
    def get_recent_activity(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent system activity for admin dashboard.
        
        Args:
            limit: Maximum number of activity items to return
        
        Returns:
            List of recent activity items
        """
        activities = []
        
        # Recent user registrations
        recent_users = db.query(User).order_by(desc(User.created_at)).limit(5).all()
        for user in recent_users:
            activities.append({
                "type": "user_registration",
                "timestamp": user.created_at,
                "description": f"New user registered: {user.name}",
                "user_id": user.id
            })
        
        # Recent group creations
        recent_groups = db.query(Group).order_by(desc(Group.created_at)).limit(5).all()
        for group in recent_groups:
            activities.append({
                "type": "group_creation",
                "timestamp": group.created_at,
                "description": f"New group created: {group.name}",
                "group_id": group.id
            })
        
        # Recent payments
        recent_payments = db.query(Payment).order_by(desc(Payment.created_at)).limit(5).all()
        for payment in recent_payments:
            activities.append({
                "type": "payment",
                "timestamp": payment.created_at,
                "description": f"Payment of ${payment.amount} - {payment.status.value}",
                "payment_id": payment.id
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def get_revenue_analytics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """
        Get revenue analytics with date filters.
        
        Args:
            start_date: Start date for analytics (defaults to 30 days ago)
            end_date: End date for analytics (defaults to today)
            group_by: Grouping period - "day", "week", or "month"
        
        Returns:
            Revenue analytics data
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Total revenue in period
        total = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        ).scalar() or 0.0
        
        # Count of successful payments
        payment_count = db.query(Payment).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        ).count()
        
        # Average payment amount
        avg_payment = total / payment_count if payment_count > 0 else 0.0
        
        # Revenue by payment type (MOMO vs CASH)
        from ..models import PaymentType
        momo_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_type == PaymentType.MOMO,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        ).scalar() or 0.0
        
        cash_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_type == PaymentType.CASH,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        ).scalar() or 0.0
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_revenue": round(total, 2),
            "payment_count": payment_count,
            "average_payment": round(avg_payment, 2),
            "revenue_by_type": {
                "momo": round(momo_revenue, 2),
                "cash": round(cash_revenue, 2)
            }
        }
    
    @staticmethod
    def get_user_analytics(db: Session) -> Dict[str, Any]:
        """
        Get user growth and engagement metrics.
        
        Returns:
            User analytics data
        """
        total_users = db.query(User).count()
        
        # User type distribution
        app_users = db.query(User).filter(User.user_type == UserType.APP).count()
        ussd_users = db.query(User).filter(User.user_type == UserType.USSD).count()
        
        # User growth over time
        now = datetime.utcnow()
        growth_data = []
        for i in range(6, -1, -1):
            period_start = now - timedelta(days=(i+1)*30)
            period_end = now - timedelta(days=i*30)
            count = db.query(User).filter(
                and_(
                    User.created_at >= period_start,
                    User.created_at < period_end
                )
            ).count()
            growth_data.append({
                "period": period_end.strftime("%Y-%m"),
                "new_users": count
            })
        
        # Active users (users with at least one payment in last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        active_users = db.query(User).join(
            Payment, User.id == Payment.user_id
        ).filter(
            Payment.created_at >= thirty_days_ago
        ).distinct().count()
        
        return {
            "total_users": total_users,
            "user_types": {
                "app": app_users,
                "ussd": ussd_users
            },
            "growth": growth_data,
            "active_users_30d": active_users,
            "activity_rate": round((active_users / total_users * 100), 2) if total_users > 0 else 0
        }
    
    @staticmethod
    def get_group_analytics(db: Session) -> Dict[str, Any]:
        """
        Get group statistics and trends.
        
        Returns:
            Group analytics data
        """
        total_groups = db.query(Group).count()
        
        # Group by status
        active_groups = db.query(Group).filter(Group.status == GroupStatus.ACTIVE).count()
        completed_groups = db.query(Group).filter(Group.status == GroupStatus.COMPLETED).count()
        suspended_groups = db.query(Group).filter(Group.status == GroupStatus.SUSPENDED).count()
        
        # Average group size
        avg_group_size = db.query(func.avg(
            db.query(Membership).filter(
                Membership.group_id == Group.id,
                Membership.is_active == True
            ).correlate(Group).count()
        )).scalar() or 0
        
        # Cash-only vs MoMo groups
        cash_only_groups = db.query(Group).filter(Group.cash_only == True).count()
        momo_groups = total_groups - cash_only_groups
        
        return {
            "total_groups": total_groups,
            "by_status": {
                "active": active_groups,
                "completed": completed_groups,
                "suspended": suspended_groups
            },
            "average_group_size": round(avg_group_size, 1),
            "payment_types": {
                "cash_only": cash_only_groups,
                "momo_enabled": momo_groups
            }
        }
    
    @staticmethod
    def export_users_csv(db: Session) -> str:
        """
        Export all users to CSV format.
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Phone Number', 'Email', 'User Type', 
            'KYC Verified', 'System Admin', 'Admin Role', 'Created At'
        ])
        
        # Write data
        users = db.query(User).all()
        for user in users:
            try:
                phone = decrypt_field(user.phone_number)
            except:
                phone = "***encrypted***"
            
            writer.writerow([
                user.id,
                user.name,
                phone,
                user.email or '',
                user.user_type.value,
                'Yes' if user.kyc_verified else 'No',
                'Yes' if user.is_system_admin else 'No',
                user.admin_role.value if user.admin_role else '',
                user.created_at.isoformat() if user.created_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_payments_csv(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Export payments to CSV format.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Transaction ID', 'User ID', 'Group ID', 'Amount',
            'Status', 'Payment Type', 'Round Number', 'Payment Date', 'Created At'
        ])
        
        # Build query
        query = db.query(Payment)
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        payments = query.all()
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.transaction_id or '',
                payment.user_id,
                payment.group_id,
                payment.amount,
                payment.status.value,
                payment.payment_type.value,
                payment.round_number,
                payment.payment_date.isoformat() if payment.payment_date else '',
                payment.created_at.isoformat() if payment.created_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def get_time_series_data(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for charts.
        
        Args:
            start_date: Start date for the series
            end_date: End date for the series
            period: Time period grouping - "day", "week", or "month"
        
        Returns:
            List of data points with date and metrics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        time_series = []
        
        # Generate series data
        current_date = start_date
        while current_date <= end_date:
            # Calculate end of period
            if period == "day":
                period_end = current_date + timedelta(days=1)
            elif period == "week":
                period_end = current_date + timedelta(weeks=1)
            else:  # month
                period_end = current_date + timedelta(days=30)
            
            # Get payments in this period
            payments = db.query(Payment).filter(
                and_(
                    Payment.created_at >= current_date,
                    Payment.created_at < period_end
                )
            ).all()
            
            successful_payments = [p for p in payments if p.status == PaymentStatus.SUCCESS]
            
            time_series.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "total_transactions": len(payments),
                "successful_transactions": len(successful_payments),
                "revenue": sum(p.amount for p in successful_payments),
                "failed_transactions": len(payments) - len(successful_payments)
            })
            
            current_date = period_end
        
        return time_series
    
    @staticmethod
    def calculate_growth_metrics(db: Session) -> Dict[str, Any]:
        """
        Calculate growth metrics (MoM, YoY).
        
        Returns:
            Growth metrics including percentage changes
        """
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        last_year = now - timedelta(days=365)
        two_months_ago = now - timedelta(days=60)
        two_years_ago = now - timedelta(days=730)
        
        # Current period revenue
        current_month_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= last_month
            )
        ).scalar() or 0.0
        
        # Previous period revenue
        previous_month_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= two_months_ago,
                Payment.payment_date < last_month
            )
        ).scalar() or 0.0
        
        # Calculate growth
        mom_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue * 100) if previous_month_revenue > 0 else 0
        
        # Current year revenue
        current_year_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= last_year
            )
        ).scalar() or 0.0
        
        # Previous year revenue
        previous_year_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= two_years_ago,
                Payment.payment_date < last_year
            )
        ).scalar() or 0.0
        
        yoy_growth = ((current_year_revenue - previous_year_revenue) / previous_year_revenue * 100) if previous_year_revenue > 0 else 0
        
        return {
            "mom_growth_percent": round(mom_growth, 2),
            "yoy_growth_percent": round(yoy_growth, 2),
            "current_month_revenue": round(current_month_revenue, 2),
            "previous_month_revenue": round(previous_month_revenue, 2),
            "current_year_revenue": round(current_year_revenue, 2),
            "previous_year_revenue": round(previous_year_revenue, 2)
        }
    
    @staticmethod
    def get_cohort_analysis(db: Session) -> List[Dict[str, Any]]:
        """
        Get user cohort retention analysis.
        
        Returns:
            Cohort analysis data showing user retention over time
        """
        cohorts = []
        now = datetime.utcnow()
        
        # Analyze cohorts over the last 6 months
        for month_offset in range(6, 0, -1):
            cohort_start = now - timedelta(days=month_offset * 30)
            cohort_end = cohort_start + timedelta(days=30)
            
            # Users registered in this cohort
            cohort_users = db.query(User).filter(
                and_(
                    User.created_at >= cohort_start,
                    User.created_at < cohort_end
                )
            ).all()
            
            cohort_size = len(cohort_users)
            
            # Check how many are still active (have made at least one payment)
            active_count = 0
            for user in cohort_users:
                has_payment = db.query(Payment).filter(
                    Payment.user_id == user.id
                ).first() is not None
                if has_payment:
                    active_count += 1
            
            retention_rate = (active_count / cohort_size * 100) if cohort_size > 0 else 0
            
            cohorts.append({
                "month": cohort_end.strftime("%Y-%m"),
                "cohort_size": cohort_size,
                "active_count": active_count,
                "retention_rate": round(retention_rate, 2)
            })
        
        return cohorts
    
    @staticmethod
    def get_financial_summary(db: Session) -> Dict[str, Any]:
        """
        Get P&L summary data.
        
        Returns:
            Financial summary with revenue and expense data
        """
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total revenue
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_date >= start_of_month
            )
        ).scalar() or 0.0
        
        # Revenue by payment type
        from ..models import PaymentType
        momo_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_type == PaymentType.MOMO,
                Payment.payment_date >= start_of_month
            )
        ).scalar() or 0.0
        
        cash_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.payment_type == PaymentType.CASH,
                Payment.payment_date >= start_of_month
            )
        ).scalar() or 0.0
        
        # Outstanding payments (pending)
        pending_amount = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.PENDING
        ).scalar() or 0.0
        
        # Failed payments count and amount
        failed_payments_query = db.query(func.count(Payment.id), func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.FAILED
        ).first()
        failed_count = failed_payments_query[0] or 0
        failed_amount = failed_payments_query[1] or 0.0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "revenue_by_type": {
                "momo": round(momo_revenue, 2),
                "cash": round(cash_revenue, 2)
            },
            "pending_amount": round(pending_amount, 2),
            "failed_payments": {
                "count": failed_count,
                "amount": round(failed_amount, 2)
            },
            "period_start": start_of_month.isoformat(),
            "period_end": now.isoformat()
        }
    
    @staticmethod
    def execute_bulk_operation(
        db: Session,
        operation_type: str,
        entity_type: str,
        entity_ids: List[int],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute bulk operations safely.
        
        Args:
            operation_type: Type of operation (deactivate, verify, retry, etc.)
            entity_type: Type of entity (user, payment, group)
            entity_ids: List of entity IDs to operate on
            params: Additional parameters for the operation
        
        Returns:
            Results of the bulk operation
        """
        results = {"processed": 0, "successful": 0, "failed": 0, "errors": []}
        
        for entity_id in entity_ids:
            try:
                if entity_type == "user":
                    if operation_type == "deactivate":
                        # Deactivate user memberships
                        db.query(Membership).filter(
                            Membership.user_id == entity_id
                        ).update({"is_active": False})
                        results["successful"] += 1
                    elif operation_type == "verify_kyc":
                        user = db.query(User).filter(User.id == entity_id).first()
                        if user:
                            user.kyc_verified = True
                            user.kyc_verified_at = datetime.utcnow()
                            results["successful"] += 1
                        else:
                            results["errors"].append(f"User {entity_id} not found")
                            results["failed"] += 1
                
                elif entity_type == "payment":
                    if operation_type == "retry":
                        payment = db.query(Payment).filter(Payment.id == entity_id).first()
                        if payment and payment.status == PaymentStatus.FAILED:
                            payment.status = PaymentStatus.PENDING
                            payment.retry_count += 1
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                
                elif entity_type == "group":
                    if operation_type == "suspend":
                        db.query(Group).filter(Group.id == entity_id).update(
                            {"status": GroupStatus.SUSPENDED}
                        )
                        results["successful"] += 1
                
                results["processed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error processing {entity_type} {entity_id}: {str(e)}")
        
        db.commit()
        return results


# Singleton instance
admin_service = AdminService()

