"""
Dual Payment Service - Handles both automated and manual payment flows.

Supports:
1. Automated payments (API User auth) - For members who want hands-off experience
2. Manual payments (bc-authorize/OAuth) - For members who want transaction control
3. USSD payments - Traditional USSD-based payments
"""

from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid
import logging

from ..models import User, Payment, PaymentStatus, PaymentPreference, PaymentMethod
from ..integrations.mtn_momo_integration import mtn_momo_service
from ..integrations.sms_sender import send_sms
from ..config import settings

logger = logging.getLogger(__name__)


class DualPaymentService:
    """
    Service to handle both automated and manual payment methods.
    """
    
    @staticmethod
    def initiate_payment(
        db: Session,
        user_id: int,
        amount: float,
        reference: str,
        description: str = "Susu contribution"
    ) -> Dict:
        """
        Initiate a payment based on user's payment preference.
        
        Args:
            db: Database session
            user_id: User ID
            amount: Payment amount
            reference: Payment reference
            description: Payment description
            
        Returns:
            Dict with payment status and details
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Get user's payment preference
        pref = db.query(PaymentPreference).filter(
            PaymentPreference.user_id == user_id
        ).first()
        
        # Default to manual if no preference set
        payment_method = pref.payment_method if pref else PaymentMethod.MANUAL
        
        # Route to appropriate payment flow
        if payment_method == PaymentMethod.AUTO:
            return DualPaymentService._process_auto_payment(
                db, user, amount, reference, description
            )
        elif payment_method == PaymentMethod.MANUAL:
            return DualPaymentService._process_manual_payment(
                db, user, amount, reference, description, pref
            )
        elif payment_method == PaymentMethod.USSD:
            return DualPaymentService._process_ussd_payment(
                db, user, amount, reference, description
            )
        else:
            return {"status": "error", "message": "Invalid payment method"}
    
    @staticmethod
    def _process_auto_payment(
        db: Session,
        user: User,
        amount: float,
        reference: str,
        description: str
    ) -> Dict:
        """
        Process automated payment (API User auth).
        
        User has pre-authorized automatic deductions.
        """
        logger.info(f"Processing AUTO payment for user {user.id}")
        
        try:
            # Request payment via MoMo
            result = mtn_momo_service.request_to_pay(
                phone_number=user.phone_number,
                amount=amount,
                reference=reference,
                payer_message=description,
                payee_note="Thank you for your contribution!"
            )
            
            if result.get("status") in ["pending", "success"]:
                # Send notification
                send_sms(
                    user.phone_number,
                    f"Payment request sent for GHS {amount:.2f}. "
                    f"Please approve on your phone. Ref: {reference}"
                )
                
                return {
                    "status": "pending",
                    "message": "Payment request sent. Awaiting approval.",
                    "reference_id": result.get("reference_id"),
                    "method": "auto"
                }
            else:
                logger.error(f"Auto payment failed: {result}")
                return {
                    "status": "error",
                    "message": result.get("message", "Payment failed"),
                    "method": "auto"
                }
                
        except Exception as e:
            logger.error(f"Auto payment error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "method": "auto"
            }
    
    @staticmethod
    def _process_manual_payment(
        db: Session,
        user: User,
        amount: float,
        reference: str,
        description: str,
        preference: Optional[PaymentPreference]
    ) -> Dict:
        """
        Process manual payment (bc-authorize/OAuth flow).
        
        User will receive a prompt and must manually approve each payment.
        """
        logger.info(f"Processing MANUAL payment for user {user.id}")
        
        try:
            # Step 1: Initiate bc-authorize flow
            auth_result = DualPaymentService._bc_authorize(
                user.phone_number,
                amount,
                reference
            )
            
            if auth_result.get("auth_req_id"):
                # Store auth request ID
                if preference:
                    preference.oauth_auth_req_id = auth_result["auth_req_id"]
                    preference.oauth_expires_at = datetime.utcnow() + timedelta(
                        seconds=auth_result.get("expires_in", 300)
                    )
                    db.commit()
                
                # Send SMS notification
                send_sms(
                    user.phone_number,
                    f"Payment request for GHS {amount:.2f}. "
                    f"Please check your MTN MoMo app to approve. Ref: {reference}"
                )
                
                return {
                    "status": "pending_approval",
                    "message": "Payment authorization sent. Please approve on your MTN MoMo app.",
                    "auth_req_id": auth_result["auth_req_id"],
                    "interval": auth_result.get("interval", 5),
                    "expires_in": auth_result.get("expires_in", 300),
                    "method": "manual"
                }
            else:
                # Fallback to simple request-to-pay
                result = mtn_momo_service.request_to_pay(
                    phone_number=user.phone_number,
                    amount=amount,
                    reference=reference,
                    payer_message=description
                )
                
                send_sms(
                    user.phone_number,
                    f"Payment request for GHS {amount:.2f}. "
                    f"Please approve the MoMo prompt. Ref: {reference}"
                )
                
                return {
                    "status": "pending",
                    "message": "Payment request sent. Please approve.",
                    "reference_id": result.get("reference_id"),
                    "method": "manual"
                }
                
        except Exception as e:
            logger.error(f"Manual payment error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "method": "manual"
            }
    
    @staticmethod
    def _process_ussd_payment(
        db: Session,
        user: User,
        amount: float,
        reference: str,
        description: str
    ) -> Dict:
        """
        Process USSD-initiated payment.
        
        User will complete payment via USSD menu.
        """
        logger.info(f"Processing USSD payment for user {user.id}")
        
        # Send SMS with USSD code
        ussd_code = settings.MTN_USSD_SERVICE_CODE
        send_sms(
            user.phone_number,
            f"Please pay GHS {amount:.2f} for {description}. "
            f"Dial {ussd_code} to make payment. Ref: {reference}"
        )
        
        return {
            "status": "pending_ussd",
            "message": f"SMS sent. User should dial {ussd_code} to pay.",
            "ussd_code": ussd_code,
            "method": "ussd"
        }
    
    @staticmethod
    def _bc_authorize(
        phone_number: str,
        amount: float,
        reference: str
    ) -> Dict:
        """
        Initiate bc-authorize flow for user consent.
        
        This uses MTN's OAuth2 bc-authorize endpoint to get user consent.
        
        Returns:
            Dict with auth_req_id, interval, expires_in
        """
        import requests
        
        try:
            # Get bearer token first
            token = mtn_momo_service._get_auth_token()
            
            url = f"{settings.MTN_MOMO_BASE_URL}/collection/v1_0/bc-authorize"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "X-Target-Environment": settings.MTN_MOMO_TARGET_ENVIRONMENT,
                "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_SUBSCRIPTION_KEY,
                "Content-Type": "application/json"
            }
            
            # Scopes for collection
            payload = {
                "login_hint": f"ID:{phone_number.replace('+', '')}",
                "scope": "profile,transfer",
                "access_type": "offline"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"bc-authorize successful: {result.get('auth_req_id')}")
            
            return {
                "auth_req_id": result.get("auth_req_id"),
                "interval": result.get("interval", 5),
                "expires_in": result.get("expires_in", 300)
            }
            
        except Exception as e:
            logger.error(f"bc-authorize error: {e}")
            # Return empty dict to trigger fallback
            return {}
    
    @staticmethod
    def check_payment_status(
        db: Session,
        reference_id: str,
        auth_req_id: Optional[str] = None
    ) -> Dict:
        """
        Check status of a payment.
        
        Handles both direct request-to-pay and bc-authorize flows.
        """
        if auth_req_id:
            # Check OAuth token endpoint for bc-authorize status
            return DualPaymentService._check_bc_authorize_status(auth_req_id)
        else:
            # Check standard transaction status
            return mtn_momo_service.get_transaction_status(reference_id)
    
    @staticmethod
    def _check_bc_authorize_status(auth_req_id: str) -> Dict:
        """Check bc-authorize status via OAuth token endpoint."""
        import requests
        
        try:
            url = f"{settings.MTN_MOMO_BASE_URL}/collection/oauth2/token/"
            
            headers = {
                "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_SUBSCRIPTION_KEY,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "urn:openid:params:grant-type:ciba",
                "auth_req_id": auth_req_id
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                # User approved!
                token_data = response.json()
                return {
                    "status": "approved",
                    "access_token": token_data.get("access_token")
                }
            elif response.status_code == 400:
                # Still pending or rejected
                error = response.json()
                if error.get("error") == "authorization_pending":
                    return {"status": "pending"}
                else:
                    return {"status": "rejected", "reason": error.get("error")}
            else:
                return {"status": "unknown"}
                
        except Exception as e:
            logger.error(f"bc-authorize status check error: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def set_payment_preference(
        db: Session,
        user_id: int,
        payment_method: PaymentMethod,
        auto_pay_day: Optional[int] = None,
        send_reminders: bool = True
    ) -> PaymentPreference:
        """
        Set or update user's payment preference.
        """
        pref = db.query(PaymentPreference).filter(
            PaymentPreference.user_id == user_id
        ).first()
        
        if not pref:
            pref = PaymentPreference(user_id=user_id)
            db.add(pref)
        
        pref.payment_method = payment_method
        pref.send_payment_reminders = send_reminders
        
        if payment_method == PaymentMethod.AUTO:
            pref.auto_pay_enabled = True
            pref.auto_pay_day = auto_pay_day or 1
            pref.momo_consent_given = True
            pref.momo_consent_date = datetime.utcnow()
        else:
            pref.auto_pay_enabled = False
        
        db.commit()
        db.refresh(pref)
        
        return pref


# Singleton instance
dual_payment_service = DualPaymentService()

