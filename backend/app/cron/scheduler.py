from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import SessionLocal
from ..services import PaymentService, PayoutService
from ..models import Group, Membership, Payment, GroupStatus
from ..config import settings


class SusuScheduler:
    """Background scheduler for automated tasks."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the scheduler with all jobs."""
        if not settings.ENABLE_SCHEDULER:
            print("Scheduler is disabled in settings")
            return
        
        # Daily payment check at 6:00 AM
        self.scheduler.add_job(
            func=self.daily_payment_check,
            trigger=CronTrigger(hour=settings.PAYMENT_CHECK_HOUR, minute=0),
            id="daily_payment_check",
            name="Daily Payment Check",
            replace_existing=True
        )
        
        # Payment retry job every 6 hours
        self.scheduler.add_job(
            func=self.retry_failed_payments,
            trigger=IntervalTrigger(hours=settings.RETRY_INTERVAL_HOURS),
            id="retry_failed_payments",
            name="Retry Failed Payments",
            replace_existing=True
        )
        
        # Payout trigger job every 2 hours
        self.scheduler.add_job(
            func=self.process_pending_payouts,
            trigger=IntervalTrigger(hours=settings.PAYOUT_CHECK_INTERVAL_HOURS),
            id="process_pending_payouts",
            name="Process Pending Payouts",
            replace_existing=True
        )
        
        self.scheduler.start()
        print("✅ Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("🛑 Scheduler stopped")
    
    @staticmethod
    def daily_payment_check():
        """
        Daily job to trigger payments for all group members.
        Runs at 6:00 AM to initiate MoMo debits.
        """
        print(f"\n🕐 Running daily payment check at {datetime.utcnow()}")
        db: Session = SessionLocal()
        
        try:
            # Get all active groups
            active_groups = db.query(Group).filter(
                Group.status == GroupStatus.ACTIVE
            ).all()
            
            for group in active_groups:
                print(f"Processing group: {group.name} (Round {group.current_round}/{group.num_cycles})")
                
                # Get all active members
                memberships = db.query(Membership).filter(
                    Membership.group_id == group.id,
                    Membership.is_active == True
                ).all()
                
                for membership in memberships:
                    # Check if member already paid for current round
                    existing_payment = db.query(Payment).filter(
                        Payment.user_id == membership.user_id,
                        Payment.group_id == group.id,
                        Payment.round_number == group.current_round,
                        Payment.status.in_(['success', 'pending'])
                    ).first()
                    
                    if existing_payment:
                        print(f"  - User {membership.user_id}: Already paid/pending")
                        continue
                    
                    # Trigger payment
                    try:
                        payment = PaymentService.process_payment(
                            db=db,
                            user_id=membership.user_id,
                            group_id=group.id,
                            round_number=group.current_round
                        )
                        print(f"  - User {membership.user_id}: Payment initiated - {payment.status}")
                    
                    except Exception as e:
                        print(f"  - User {membership.user_id}: Payment failed - {str(e)}")
                        continue
            
            print(f"✅ Daily payment check completed\n")
        
        except Exception as e:
            print(f"❌ Error in daily payment check: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    def retry_failed_payments():
        """
        Retry failed payments (max 3 attempts).
        Runs every 6 hours.
        """
        print(f"\n🔄 Running payment retry job at {datetime.utcnow()}")
        db: Session = SessionLocal()
        
        try:
            failed_payments = PaymentService.get_failed_payments_for_retry(db)
            
            print(f"Found {len(failed_payments)} failed payments to retry")
            
            for payment in failed_payments:
                try:
                    PaymentService.retry_failed_payment(db, payment.id)
                    print(f"  - Payment {payment.id}: Retry successful")
                
                except Exception as e:
                    print(f"  - Payment {payment.id}: Retry failed - {str(e)}")
                    continue
            
            print(f"✅ Payment retry job completed\n")
        
        except Exception as e:
            print(f"❌ Error in payment retry job: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    def process_pending_payouts():
        """
        Check for completed rounds and process payouts.
        Runs every 2 hours.
        """
        print(f"\n💰 Running payout processing job at {datetime.utcnow()}")
        db: Session = SessionLocal()
        
        try:
            # Get all active groups
            active_groups = db.query(Group).filter(
                Group.status == GroupStatus.ACTIVE
            ).all()
            
            for group in active_groups:
                # Check if current round is complete
                round_complete = PayoutService.check_round_complete(
                    db, group.id, group.current_round
                )
                
                if round_complete:
                    print(f"Group {group.name}: Round {group.current_round} complete")
                    
                    # Create payout if it doesn't exist
                    payout = PayoutService.create_payout_for_round(
                        db, group.id, group.current_round
                    )
                    
                    if payout:
                        print(f"  - Payout created: ID {payout.id}, Status: {payout.status}")
                        
                        # Auto-process payout
                        try:
                            PayoutService.execute_payout(db, payout.id)
                            print(f"  - Payout executed successfully")
                        
                        except Exception as e:
                            print(f"  - Payout execution failed: {str(e)}")
            
            print(f"✅ Payout processing job completed\n")
        
        except Exception as e:
            print(f"❌ Error in payout processing job: {str(e)}")
        
        finally:
            db.close()


# Global scheduler instance
scheduler = SusuScheduler()

