# 🎉 Dual Payment System - Implementation Guide

## Overview

Your SusuSave now supports **three payment methods**, giving members the freedom to choose:

1. **🤖 Automated** - Set it and forget it (API User auth)
2. **👤 Manual** - Approve each payment (bc-authorize/OAuth)
3. **📱 USSD** - Traditional dial-code payments

## 🚀 Quick Start

### Step 1: Run Database Migration

```bash
cd /Users/maham/susu/backend
source venv/bin/activate

# Run migration to create payment_preferences table
alembic upgrade head
```

### Step 2: Update Your Registration Flow

**Mobile App Example:**

```python
from app.services.dual_payment_service import dual_payment_service
from app.models import PaymentMethod

@router.post("/auth/register")
def register(user_data: dict, db: Session = Depends(get_db)):
    # Create user
    user = User(
        phone_number=user_data["phone_number"],
        name=user_data["name"],
        email=user_data.get("email")
    )
    db.add(user)
    db.commit()
    
    # Set payment preference (user chose during signup)
    dual_payment_service.set_payment_preference(
        db=db,
        user_id=user.id,
        payment_method=user_data.get("payment_method", PaymentMethod.MANUAL),
        auto_pay_day=user_data.get("auto_pay_day", 1),
        send_reminders=True
    )
    
    return {"message": "Registration successful", "user_id": user.id}
```

**USSD Registration Example:**

```python
# In your USSD service
def handle_registration_payment_choice(session_id, phone_number, choice):
    if choice == "1":
        method = PaymentMethod.AUTO
        msg = "CON Great! Auto-pay selected.\nOn what day of month?\n(1-31)"
    elif choice == "2":
        method = PaymentMethod.MANUAL
        msg = "END Manual approval selected! You'll approve each payment."
    elif choice == "3":
        method = PaymentMethod.USSD
        msg = "END USSD payment selected! Dial *920*55# to pay."
    
    # Save preference
    dual_payment_service.set_payment_preference(
        db=db,
        user_id=user_id,
        payment_method=method
    )
    
    return msg
```

### Step 3: Process Payments with Dual System

```python
from app.services.dual_payment_service import dual_payment_service

# When it's time to collect payments
def collect_monthly_contribution(db, membership_id):
    membership = db.query(Membership).get(membership_id)
    user = membership.user
    group = membership.group
    
    # Automatically routes to user's preferred method!
    result = dual_payment_service.initiate_payment(
        db=db,
        user_id=user.id,
        amount=group.contribution_amount,
        reference=f"SUSU_{group.id}_R{group.current_round}_U{user.id}",
        description=f"{group.name} contribution - Round {group.current_round}"
    )
    
    if result['status'] == 'pending':
        # AUTO payment: User will receive MoMo prompt
        print(f"✅ Auto payment request sent to {user.name}")
        
    elif result['status'] == 'pending_approval':
        # MANUAL payment: User must approve via bc-authorize
        print(f"⏳ Manual approval required from {user.name}")
        print(f"   Auth Request ID: {result['auth_req_id']}")
        
    elif result['status'] == 'pending_ussd':
        # USSD payment: User should dial code
        print(f"📱 USSD payment SMS sent to {user.name}")
        
    else:
        # Error
        print(f"❌ Payment failed: {result['message']}")
    
    return result
```

### Step 4: Check Payment Status

```python
# Poll for payment status (especially for manual/bc-authorize)
def check_and_update_payment_status(db, payment_id):
    payment = db.query(Payment).get(payment_id)
    
    # Check status based on payment method
    if payment.oauth_auth_req_id:
        # Manual payment with bc-authorize
        status = dual_payment_service.check_payment_status(
            db=db,
            reference_id=None,
            auth_req_id=payment.oauth_auth_req_id
        )
    else:
        # Auto or standard payment
        status = dual_payment_service.check_payment_status(
            db=db,
            reference_id=payment.momo_transaction_id
        )
    
    # Update payment record
    if status['status'] == 'successful' or status['status'] == 'approved':
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        
        # Send confirmation
        send_payment_confirmation(
            payment.user.phone_number,
            payment.amount,
            payment.group.name,
            payment.group.current_round
        )
    
    elif status['status'] == 'failed' or status['status'] == 'rejected':
        payment.status = PaymentStatus.FAILED
        
        # Notify user
        send_sms(
            payment.user.phone_number,
            f"Payment of GHS {payment.amount} failed. "
            f"Please retry via USSD: *920*55#"
        )
    
    db.commit()
    return status
```

## 📱 Frontend Integration

### React Native - Payment Method Selector

```typescript
import React, { useState } from 'react';
import { View, TouchableOpacity, Text } from 'react-native';

function PaymentMethodSelector({ onSelect }) {
  const [selected, setSelected] = useState('auto');
  
  const methods = [
    {
      id: 'auto',
      title: 'Automated (Recommended)',
      description: 'Set it once, we handle the rest',
      icon: '🤖',
      badge: 'Popular'
    },
    {
      id: 'manual',
      title: 'Manual Approval',
      description: 'Review each payment',
      icon: '👤'
    },
    {
      id: 'ussd',
      title: 'USSD Payment',
      description: 'Dial *920*55# to pay',
      icon: '📱'
    }
  ];
  
  return (
    <View>
      <Text style={styles.title}>Choose Payment Method</Text>
      {methods.map(method => (
        <TouchableOpacity
          key={method.id}
          onPress={() => {
            setSelected(method.id);
            onSelect(method.id);
          }}
          style={[
            styles.card,
            selected === method.id && styles.selected
          ]}
        >
          <Text style={styles.icon}>{method.icon}</Text>
          <Text style={styles.methodTitle}>{method.title}</Text>
          <Text style={styles.description}>{method.description}</Text>
          {method.badge && (
            <View style={styles.badge}>
              <Text>{method.badge}</Text>
            </View>
          )}
        </TouchableOpacity>
      ))}
    </View>
  );
}
```

### USSD Menu Flow

```
# Main menu after login
CON Welcome John!
1. My Groups
2. Make Payment
3. Settings
4. Help

# User selects 3 (Settings)

CON Settings
1. Payment method
2. Profile
3. Notifications
0. Back

# User selects 1

CON Current: Automated
Change to:
1. Manual approval
2. USSD payments
3. Keep current
0. Back

# User makes selection

END Payment method updated!
You chose: Manual approval
Changes take effect next month.
```

## 🔄 Scheduled Tasks

### Cron Job for Auto Payments

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.dual_payment_service import dual_payment_service

def collect_auto_payments():
    """
    Run daily to collect payments from users with auto-pay enabled.
    """
    db = SessionLocal()
    
    try:
        # Get all active memberships with auto-pay
        today = datetime.now().day
        
        prefs = db.query(PaymentPreference).filter(
            PaymentPreference.auto_pay_enabled == True,
            PaymentPreference.auto_pay_day == today
        ).all()
        
        for pref in prefs:
            user = pref.user
            # Get user's active groups
            for membership in user.memberships:
                if membership.is_active:
                    # Initiate payment
                    result = dual_payment_service.initiate_payment(
                        db=db,
                        user_id=user.id,
                        amount=membership.group.contribution_amount,
                        reference=f"AUTO_{membership.group_id}_R{membership.group.current_round}",
                        description=f"Auto-pay: {membership.group.name}"
                    )
                    
                    logger.info(f"Auto-pay initiated for user {user.id}: {result['status']}")
        
    finally:
        db.close()

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(collect_auto_payments, 'cron', hour=9)  # Run daily at 9 AM
scheduler.start()
```

### Poll bc-authorize Status

```python
def poll_pending_authorizations():
    """
    Poll for status of pending bc-authorize requests.
    Run every 5 minutes.
    """
    db = SessionLocal()
    
    try:
        # Get preferences with pending OAuth requests
        now = datetime.utcnow()
        
        prefs = db.query(PaymentPreference).filter(
            PaymentPreference.oauth_auth_req_id.isnot(None),
            PaymentPreference.oauth_expires_at > now
        ).all()
        
        for pref in prefs:
            # Check status
            status = dual_payment_service._check_bc_authorize_status(
                pref.oauth_auth_req_id
            )
            
            if status['status'] == 'approved':
                # User approved! Process payment
                logger.info(f"User {pref.user_id} approved payment")
                # TODO: Complete the payment transaction
                
                # Clear OAuth request
                pref.oauth_auth_req_id = None
                pref.oauth_expires_at = None
                db.commit()
                
            elif status['status'] == 'rejected':
                # User rejected
                logger.warning(f"User {pref.user_id} rejected payment")
                pref.oauth_auth_req_id = None
                pref.oauth_expires_at = None
                db.commit()
        
    finally:
        db.close()

scheduler.add_job(poll_pending_authorizations, 'interval', minutes=5)
```

## 📊 Analytics Dashboard

```python
def get_payment_method_analytics(db):
    """Get insights on payment method usage and success rates."""
    
    from sqlalchemy import func
    
    # Count by payment method
    method_counts = db.query(
        PaymentPreference.payment_method,
        func.count(PaymentPreference.id)
    ).group_by(PaymentPreference.payment_method).all()
    
    # Success rates
    # TODO: Join with payments table to calculate success rates
    
    return {
        'distribution': {
            method: count for method, count in method_counts
        },
        'total_users': sum(count for _, count in method_counts),
        'auto_enabled': db.query(PaymentPreference).filter(
            PaymentPreference.auto_pay_enabled == True
        ).count()
    }
```

## 🔔 Notification Templates

### Auto Payment

```python
def send_auto_payment_notification(user, amount, group_name):
    send_sms(
        user.phone_number,
        f"💰 Auto-pay reminder: GHS {amount:.2f} for {group_name} "
        f"will be requested today. Check your phone for MoMo prompt to approve."
    )
```

### Manual Payment

```python
def send_manual_payment_request(user, amount, group_name, auth_req_id):
    send_sms(
        user.phone_number,
        f"📱 Payment request: GHS {amount:.2f} for {group_name}. "
        f"Open your MTN MoMo app to review and approve."
    )
```

### USSD Payment

```python
def send_ussd_payment_reminder(user, amount, group_name, reference):
    send_sms(
        user.phone_number,
        f"📞 Payment due: GHS {amount:.2f} for {group_name}. "
        f"Dial *920*55# → Make Payment → Enter ref: {reference}"
    )
```

## ✅ Testing Checklist

- [ ] Database migration runs successfully
- [ ] Users can select payment method during signup
- [ ] AUTO payments initiate correctly
- [ ] MANUAL payments trigger bc-authorize flow
- [ ] USSD payments send correct SMS
- [ ] Payment status polling works
- [ ] Users can change payment method in settings
- [ ] Notifications sent for each method
- [ ] Analytics dashboard shows correct stats
- [ ] Cron jobs run on schedule

## 🚀 Deployment Steps

1. **Run migration**: `alembic upgrade head`
2. **Test in sandbox**: Verify all three methods work
3. **Update mobile app**: Add payment method selector to signup
4. **Update USSD menus**: Add payment method selection
5. **Enable cron jobs**: Start auto-payment scheduler
6. **Monitor**: Watch logs for any issues
7. **Gradual rollout**: Start with new users, then migrate existing

## 📚 Additional Resources

- **Full Documentation**: `/Users/maham/susu/backend/docs/DUAL_PAYMENT_SYSTEM.md`
- **MTN MoMo Setup**: `/Users/maham/susu/backend/docs/MTN_SETUP.md`
- **Service Code**: `/Users/maham/susu/backend/app/services/dual_payment_service.py`
- **Models**: `/Users/maham/susu/backend/app/models/payment_preference.py`

---

**Status**: ✅ Ready for Implementation  
**Version**: 1.0.0  
**Last Updated**: October 22, 2025

