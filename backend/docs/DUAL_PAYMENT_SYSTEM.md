

# Dual Payment System - Member Choice

Give your susu members the flexibility to choose their payment method!

## 🎯 Overview

SusuSave supports **three payment methods**, allowing members to choose what works best for them:

### 1. 🤖 Automated Payments (Recommended)
**Best for:** Busy professionals who want hands-off convenience

**How it works:**
1. Member authorizes automatic payments during signup
2. System sends payment request each month automatically
3. Member receives MoMo prompt and approves on phone
4. Payment processed, SMS confirmation sent
5. No need to remember payment dates!

**User Experience:**
```
Month 1: Member joins → Authorizes auto-pay → Done!
Month 2-12: Automatic request → Approve on phone → Done!
```

###  2. 👤 Manual Approval (bc-authorize)
**Best for:** Members who want control over each transaction

**How it works:**
1. Member chooses manual payment during signup
2. System sends payment request when due
3. Member gets notification on MTN MoMo app
4. Member reviews and approves the payment
5. Full transparency on every transaction

**User Experience:**
```
Each month: SMS reminder → MoMo app notification → Review → Approve → Done!
```

### 3. 📱 USSD Payment
**Best for:** Traditional users comfortable with USSD

**How it works:**
1. Member receives SMS reminder with USSD code
2. Member dials *920*55# and follows menu
3. Selects "Make Payment"
4. Enters amount and confirms
5. Payment processed

**User Experience:**
```
Each month: SMS reminder → Dial *920*55# → Follow menu → Pay → Done!
```

## 📊 Comparison Table

| Feature | Auto | Manual | USSD |
|---------|------|--------|------|
| **Setup Time** | One-time auth | Choose per transaction | No setup |
| **Monthly Effort** | Just approve prompt | Review & approve | Dial code & pay |
| **Reminders** | Automatic | SMS + App notification | SMS only |
| **Control** | Medium | High | High |
| **Convenience** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Tech Required** | Smartphone | Smartphone | Any phone |

## 💻 Implementation

### Database Schema

```sql
CREATE TABLE payment_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    payment_method VARCHAR(20) NOT NULL DEFAULT 'manual',
    auto_pay_enabled BOOLEAN DEFAULT FALSE,
    auto_pay_day INTEGER,  -- Day of month (1-31)
    send_payment_reminders BOOLEAN DEFAULT TRUE,
    reminder_days_before INTEGER DEFAULT 3,
    momo_consent_given BOOLEAN DEFAULT FALSE,
    momo_consent_date TIMESTAMP,
    oauth_auth_req_id VARCHAR(255),
    oauth_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### User Signup Flow

**Mobile App:**
```python
from app.services.dual_payment_service import dual_payment_service
from app.models import PaymentMethod

# During signup, show payment method options
def register_user(db, user_data):
    # Create user
    user = User(**user_data)
    db.add(user)
    db.commit()
    
    # Set payment preference based on user choice
    payment_method = user_data.get('payment_method', PaymentMethod.MANUAL)
    
    dual_payment_service.set_payment_preference(
        db=db,
        user_id=user.id,
        payment_method=payment_method,
        auto_pay_day=user_data.get('auto_pay_day', 1),
        send_reminders=True
    )
    
    return user
```

**USSD Flow:**
```
CON Welcome to SusuSave
1. Register
2. Login

# User selects 1

CON Enter your name:
# User enters name

CON Choose payment method:
1. Auto (recommended)
2. Manual approval
3. USSD payment

# User selects preference

CON Great! You chose [method]
Registration complete!
```

### Processing Payments

```python
from app.services.dual_payment_service import dual_payment_service

# Monthly payment collection
def collect_monthly_payments(db):
    # Get all active members whose payment is due
    members_due = get_members_with_payment_due(db)
    
    for member in members_due:
        # Service automatically routes to correct payment method
        result = dual_payment_service.initiate_payment(
            db=db,
            user_id=member.id,
            amount=member.group.contribution_amount,
            reference=f"SUSU_{member.group_id}_R{member.group.current_round}",
            description=f"{member.group.name} - Round {member.group.current_round}"
        )
        
        if result['status'] == 'pending':
            print(f"✅ Payment request sent to {member.name} via {result['method']}")
        elif result['status'] == 'pending_approval':
            print(f"⏳ Awaiting {member.name}'s approval (auth_req_id: {result['auth_req_id']})")
        else:
            print(f"❌ Payment failed for {member.name}: {result['message']}")
```

### Checking Payment Status

```python
# For automated/manual payments
def check_payment_status(db, payment_reference):
    status = dual_payment_service.check_payment_status(
        db=db,
        reference_id=payment_reference
    )
    
    if status['status'] == 'successful':
        # Mark payment as completed
        update_payment_status(db, payment_reference, PaymentStatus.COMPLETED)
        send_confirmation_sms(user)
    elif status['status'] == 'pending':
        # Still waiting for approval
        pass
    elif status['status'] == 'failed':
        # Handle failure
        notify_admin(user, "Payment failed")
```

## 🎨 User Interface Examples

### Mobile App - Payment Method Selection

```typescript
// React Native signup screen
function PaymentMethodSelector() {
  return (
    <View>
      <Text>Choose Your Payment Method</Text>
      
      <TouchableOpacity onPress={() => setMethod('auto')}>
        <Card>
          <Icon name="automation" />
          <Title>Automated (Recommended)</Title>
          <Description>
            Set it and forget it! We'll remind you each month.
          </Description>
          <Badge>Most Popular</Badge>
        </Card>
      </TouchableOpacity>
      
      <TouchableOpacity onPress={() => setMethod('manual')}>
        <Card>
          <Icon name="hand" />
          <Title>Manual Approval</Title>
          <Description>
            Review and approve each payment manually.
          </Description>
        </Card>
      </TouchableOpacity>
      
      <TouchableOpacity onPress={() => setMethod('ussd')}>
        <Card>
          <Icon name="phone" />
          <Title>USSD Payment</Title>
          <Description>
            Pay via *920*55# when reminded.
          </Description>
        </Card>
      </TouchableOpacity>
    </View>
  );
}
```

### USSD Menu

```
CON SusuSave - Settings
1. View my groups
2. Payment settings
3. Profile

# User selects 2

CON Payment Settings
Current: Automated
1. Switch to Manual
2. Switch to USSD
3. Set payment day
0. Back

# User selects payment preference
```

## 🔄 Migration Guide

### For Existing Users

```python
# Database migration to add payment preferences
def migrate_existing_users(db):
    """Set default payment preference for existing users."""
    users = db.query(User).all()
    
    for user in users:
        if not user.payment_preference:
            # Default to manual for safety
            dual_payment_service.set_payment_preference(
                db=db,
                user_id=user.id,
                payment_method=PaymentMethod.MANUAL,
                send_reminders=True
            )
    
    db.commit()
    print(f"✅ Migrated {len(users)} users to dual payment system")
```

### Alembic Migration Script

```python
"""add payment preferences

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-10-22

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create payment_preferences table
    op.create_table(
        'payment_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_method', sa.String(), nullable=False, server_default='manual'),
        sa.Column('auto_pay_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('auto_pay_day', sa.Integer(), nullable=True),
        sa.Column('send_payment_reminders', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('reminder_days_before', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('momo_consent_given', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('momo_consent_date', sa.DateTime(), nullable=True),
        sa.Column('oauth_auth_req_id', sa.String(), nullable=True),
        sa.Column('oauth_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

def downgrade():
    op.drop_table('payment_preferences')
```

## 📱 SMS Templates

### For Automated Payments
```
✅ AUTO-PAY SETUP
Your automated payments are now active! We'll request GHS 50.00 on the 1st of each month. Simply approve the MoMo prompt. Easy! 🎉

📱 PAYMENT DUE
Auto-pay reminder: GHS 50.00 for Family Susu due today. Check your phone for MoMo prompt to approve. Ref: SUSU_001_R5

✅ PAYMENT CONFIRMED
Payment received! GHS 50.00 for Family Susu - Round 5. Thank you!
```

### For Manual Approval
```
📱 PAYMENT REQUEST
Please approve payment of GHS 50.00 for Family Susu. Check your MTN MoMo app to review and approve. Ref: SUSU_001_R5

⏰ REMINDER
Payment of GHS 50.00 still pending. Please check your MoMo app to approve. Due in 2 days. Ref: SUSU_001_R5

✅ PAYMENT CONFIRMED
Payment approved! GHS 50.00 for Family Susu - Round 5. Thank you!
```

### For USSD Payments
```
📱 PAYMENT DUE
Please pay GHS 50.00 for Family Susu. Dial *920*55# → Select "Make Payment" → Enter reference: SUSU_001_R5

⏰ REMINDER
Payment still pending: GHS 50.00. Dial *920*55# to pay. Due in 2 days. Ref: SUSU_001_R5

✅ PAYMENT CONFIRMED
Payment received! GHS 50.00 for Family Susu - Round 5. Thank you!
```

## 🔐 Security & Consent

### For Automated Payments
```python
# During auto-pay setup, ensure explicit consent
def setup_auto_pay(db, user_id):
    # Show consent screen
    consent_text = """
    By enabling automated payments:
    - You authorize SusuSave to request monthly contributions
    - You will receive a MoMo prompt to approve each payment
    - You can disable auto-pay anytime in settings
    - Your payment information is encrypted and secure
    """
    
    # User must explicitly agree
    if user_agrees:
        dual_payment_service.set_payment_preference(
            db=db,
            user_id=user_id,
            payment_method=PaymentMethod.AUTO,
            auto_pay_day=chosen_day
        )
        
        # Log consent for compliance
        log_user_consent(user_id, "auto_pay", consent_text)
```

## 📊 Analytics & Reporting

```python
def get_payment_method_stats(db):
    """Get statistics on payment method usage."""
    prefs = db.query(PaymentPreference).all()
    
    stats = {
        'auto': len([p for p in prefs if p.payment_method == PaymentMethod.AUTO]),
        'manual': len([p for p in prefs if p.payment_method == PaymentMethod.MANUAL]),
        'ussd': len([p for p in prefs if p.payment_method == PaymentMethod.USSD]),
        'total': len(prefs)
    }
    
    # Calculate success rates per method
    # ... implementation
    
    return stats
```

## 🎯 Best Practices

1. **Default to Manual**: For safety, default new users to manual approval
2. **Clear Communication**: Explain each payment method clearly during signup
3. **Easy Switching**: Allow users to change payment method anytime
4. **Consent Tracking**: Log when users authorize automated payments
5. **Grace Period**: Give users time to approve before marking as late
6. **Retry Logic**: Auto-retry failed payments after 24 hours
7. **Notifications**: Send reminders for pending payments
8. **Analytics**: Track which payment methods have highest success rates

## 🚀 Future Enhancements

- **Payment Schedules**: Custom payment dates per group
- **Split Payments**: Allow partial payments
- **Payment Plans**: Flexible payment arrangements
- **Reward Programs**: Incentives for on-time payments
- **Group Preferences**: Group-level payment method requirements
- **Bank Integration**: Direct bank debit option
- **Card Payments**: Credit/debit card as backup method

---

**Implementation Status**: ✅ Ready to use
**Last Updated**: October 22, 2025
**Version**: 1.0.0

