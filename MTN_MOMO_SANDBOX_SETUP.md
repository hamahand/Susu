# 🏦 MTN MoMo Sandbox Setup & Payment Flow Guide

**Complete guide to set up MTN Mobile Money sandbox and implement the payment flow**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Payment Flow Implementation](#payment-flow-implementation)
5. [Testing Guide](#testing-guide)
6. [Admin Features](#admin-features)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This guide helps you:
- ✅ Set up MTN MoMo sandbox for testing
- ✅ Enable user-initiated payments (click unpaid → pay)
- ✅ Enable admin-initiated payments (admin triggers payment for members)
- ✅ Test the complete payment flow

### What You'll Build

**User Flow:**
1. User sees unpaid contribution in dashboard
2. Clicks "Pay Now" button
3. Receives MoMo prompt on phone
4. Approves payment
5. Payment marked as paid

**Admin Flow:**
1. Admin sees member with unpaid contribution
2. Clicks "Request Payment" on member
3. Member receives MoMo prompt
4. Member approves
5. Admin sees status update

---

## Quick Start

### 1. Get MTN MoMo Subscription Key

1. Go to https://momodeveloper.mtn.com/
2. Sign up / Log in
3. Subscribe to **Collections** product
4. Copy your **Primary Key** (Subscription Key)

### 2. Run Setup Script

```bash
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py
```

Enter your:
- Subscription Key
- Callback Host (your ngrok URL or domain)

**Script will:**
- ✅ Create API User
- ✅ Generate API Key
- ✅ Test authentication
- ✅ Update .env file

### 3. Restart Backend

```bash
cd /Users/maham/susu
docker-compose restart backend
```

### 4. Test Payment Flow

```bash
# Test endpoint
curl -X POST http://localhost:8000/payments/admin/request-payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "group_id": 1,
    "user_id": 2,
    "round_number": 1
  }'
```

**Done! 🎉** Now members can pay via MoMo.

---

## Detailed Setup

### Step 1: Register at MTN MoMo Developer Portal

#### 1.1 Create Account

```
URL: https://momodeveloper.mtn.com/
```

1. Click "Sign Up"
2. Fill in details:
   - Email
   - Password
   - Country: Ghana
   - Phone number
3. Verify email
4. Log in to dashboard

#### 1.2 Subscribe to Collections API

1. Click **"Products"** in dashboard
2. Find **"Collection"** product
3. Click **"Subscribe"**
4. Copy your **Primary Key** (this is your Subscription Key)

**Save this key!** You'll need it.

```
Example: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Step 2: Create Sandbox Credentials

#### Option A: Use Setup Script (Recommended)

```bash
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py
```

The script will:
1. Ask for your Subscription Key
2. Ask for your callback host
3. Create API User
4. Generate API Key
5. Test authentication
6. Update your .env file

**Example Session:**
```
======================================================================
MTN MoMo Sandbox Setup
======================================================================

Enter your Collection Subscription Key: a1b2c3d4e5f6...
Enter callback host (default: your-app.ngrok-free.app): abc123.ngrok-free.app

✓ Subscription Key: a1b2c3d4e5...
✓ Callback Host: abc123.ngrok-free.app

----------------------------------------------------------------------
Step 1: Creating API User
----------------------------------------------------------------------

✅ API User created successfully!
   API User ID: 12345678-1234-1234-1234-123456789012

----------------------------------------------------------------------
Step 2: Creating API Key
----------------------------------------------------------------------

✅ API Key created successfully!
   API Key: abcdef1234567890abcdef1234567890

----------------------------------------------------------------------
Step 3: Testing Authentication
----------------------------------------------------------------------

✅ Authentication successful!
   Access Token: eyJ0eXAiOiJKV1QiLCJ...

----------------------------------------------------------------------
Step 4: Updating .env File
----------------------------------------------------------------------

✅ Updated /Users/maham/susu/backend/.env

======================================================================
Setup Complete! 🎉
======================================================================
```

#### Option B: Manual Setup (via API)

If you prefer manual setup:

```bash
# Set your subscription key
SUBSCRIPTION_KEY="your_subscription_key_here"

# 1. Generate API User ID
API_USER=$(uuidgen)

# 2. Create API User
curl -X POST https://sandbox.momodeveloper.mtn.com/v1_0/apiuser \
  -H "X-Reference-Id: $API_USER" \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "providerCallbackHost": "your-callback-host.com"
  }'

# 3. Create API Key
curl -X POST "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser/$API_USER/apikey" \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY"

# Response will contain your API Key
```

### Step 3: Configure Environment

Edit `/Users/maham/susu/backend/.env`:

```env
# MTN Mobile Money Configuration
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key_from_portal
MTN_MOMO_API_USER=your_api_user_uuid
MTN_MOMO_API_KEY=your_api_key_from_creation
MTN_MOMO_TARGET_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_CURRENCY=GHS

# Enable MTN Services
ENABLE_MTN_MOMO=true
USE_MTN_SERVICES=true
```

### Step 4: Set Up Public Callback URL

MTN needs to reach your server. Use ngrok:

```bash
# Install ngrok
brew install ngrok

# Start ngrok
ngrok http 8000
```

**Copy the https URL:**
```
https://abc123.ngrok-free.app
```

**Update .env:**
```env
MTN_CALLBACK_URL=https://abc123.ngrok-free.app/ussd/callback
```

### Step 5: Test Authentication

```bash
cd /Users/maham/susu/backend

# Test getting auth token
python3 << EOF
from app.integrations.mtn_momo_integration import mtn_momo_service

try:
    token = mtn_momo_service._get_auth_token()
    print(f"✅ Authentication successful!")
    print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

**Expected Output:**
```
✅ Authentication successful!
Token: eyJ0eXAiOiJKV1QiLCJh...
```

---

## Payment Flow Implementation

### Backend Endpoints

#### 1. User Initiates Payment (Already Exists)

**Endpoint:** `POST /payments/{payment_id}/pay-now`

**Frontend Usage:**
```typescript
// User clicks "Pay Now" on unpaid contribution
const handlePayNow = async (paymentId: number) => {
  try {
    const result = await apiClient.post(`/payments/${paymentId}/pay-now`);
    alert('Payment request sent! Check your phone for MoMo prompt.');
  } catch (error) {
    alert('Failed to initiate payment');
  }
};
```

#### 2. Admin Requests Payment for Member (New)

Let me create this endpoint:

```python
# backend/app/routers/payments.py

@router.post("/admin/request-payment", response_model=PaymentResponse)
def admin_request_payment(
    payment_data: AdminPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin requests payment from a group member.
    Only group admin can trigger this.
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
```

#### 3. Check Payment Status

**Endpoint:** `GET /payments/{payment_id}/status`

```python
@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
def check_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check status of a payment request."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(404, "Payment not found")
    
    # Get MTN transaction status if it exists
    if payment.transaction_id:
        mtn_status = mtn_momo_service.get_transaction_status(payment.transaction_id)
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "mtn_status": mtn_status.get("status"),
            "amount": payment.amount,
            "transaction_id": payment.transaction_id
        }
    
    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": payment.amount
    }
```

### Frontend Components

#### 1. Payment Button Component

Create `/Users/maham/susu/web/app/src/components/PaymentButton.tsx`:

```typescript
import React, { useState } from 'react';
import { Button } from './Button';
import apiClient from '../api/client';

interface PaymentButtonProps {
  paymentId?: number;
  groupId: number;
  userId: number;
  roundNumber: number;
  amount: number;
  isAdmin?: boolean;
  onSuccess?: () => void;
}

export const PaymentButton: React.FC<PaymentButtonProps> = ({
  paymentId,
  groupId,
  userId,
  roundNumber,
  amount,
  isAdmin = false,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);
    try {
      let result;
      
      if (paymentId) {
        // User pays their own payment
        result = await apiClient.post(`/payments/${paymentId}/pay-now`);
      } else if (isAdmin) {
        // Admin requests payment from member
        result = await apiClient.post('/payments/admin/request-payment', {
          group_id: groupId,
          user_id: userId,
          round_number: roundNumber
        });
      }
      
      alert('Payment request sent! User will receive MoMo prompt on their phone.');
      onSuccess?.();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      onClick={handlePayment}
      loading={loading}
      size="small"
      variant={isAdmin ? "outline" : "primary"}
    >
      {isAdmin ? '📱 Request Payment' : '💳 Pay Now'}
    </Button>
  );
};
```

#### 2. Update GroupDashboardPage

Update `/Users/maham/susu/web/app/src/pages/GroupDashboardPage.tsx`:

```typescript
// Add import
import { PaymentButton } from '../components/PaymentButton';

// In the Members List section, update the member item:
<div key={member.user_id} className="member-item">
  <div className="member-left">
    <div className="member-position">{member.rotation_position}</div>
    <div className="member-info">
      <div className="member-name">
        {member.name} {member.is_admin && '👑'}
      </div>
      <div className="member-phone">{member.phone_number}</div>
    </div>
  </div>
  
  <div className="member-right">
    {member.paid_current_round ? (
      <StatusBadge status="paid" size="small" />
    ) : (
      <div className="member-actions">
        <StatusBadge status="unpaid" size="small" />
        
        {/* Show Pay Now button if it's current user */}
        {member.user_id === currentUser.id && (
          <PaymentButton
            groupId={group.id}
            userId={member.user_id}
            roundNumber={group.current_round}
            amount={group.contribution_amount}
            onSuccess={handleRefresh}
          />
        )}
        
        {/* Show Request Payment if admin and not current user */}
        {isAdmin && member.user_id !== currentUser.id && (
          <PaymentButton
            groupId={group.id}
            userId={member.user_id}
            roundNumber={group.current_round}
            amount={group.contribution_amount}
            isAdmin={true}
            onSuccess={handleRefresh}
          />
        )}
      </div>
    )}
  </div>
</div>
```

---

## Testing Guide

### 1. Test Sandbox Numbers

MTN provides test phone numbers that auto-approve/reject:

**Auto-Approve Numbers:**
```
233240000001
233240000002
233240000003
...
233240000099
```

**Auto-Reject Numbers:**
```
233240000100
233240000101
...
233240000199
```

### 2. Test Payment Flow

#### Test 1: User Pays Their Own Contribution

```bash
# 1. Login as a member
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233240000001",
    "password": "password123"
  }'

# Save the token

# 2. Get their pending payment
curl http://localhost:8000/payments/my-payments \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Pay the payment
curl -X POST http://localhost:8000/payments/{payment_id}/pay-now \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Check status
curl http://localhost:8000/payments/{payment_id}/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Test 2: Admin Requests Payment from Member

```bash
# 1. Login as admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233598430399",
    "password": "admin123"
  }'

# 2. Request payment from member
curl -X POST http://localhost:8000/payments/admin/request-payment \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "user_id": 2,
    "round_number": 1
  }'

# 3. Check payment status
curl http://localhost:8000/payments/{payment_id}/status \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 3. Test with Frontend

#### User Flow:
1. Login to web app
2. Go to group dashboard
3. See your unpaid contribution
4. Click "Pay Now"
5. Check logs for MoMo request

#### Admin Flow:
1. Login as group admin
2. Go to group dashboard
3. See member with unpaid status
4. Click "Request Payment" next to their name
5. Member receives MoMo prompt

### 4. Monitor Payment Status

```bash
# Watch backend logs
docker logs sususave_backend --tail 50 --follow

# Look for:
# ✅ "Payment request sent: {reference_id}"
# ✅ "Successfully obtained MTN MoMo access token"
# ❌ Any error messages
```

---

## Admin Features

### 1. Request Payment from Member

**Use Case:** Member forgot to pay, admin reminds them

```typescript
// Frontend usage
const handleRequestPayment = async (memberId: number) => {
  try {
    await apiClient.post('/payments/admin/request-payment', {
      group_id: groupId,
      user_id: memberId,
      round_number: currentRound
    });
    
    alert('Payment request sent to member!');
  } catch (error) {
    alert('Failed to send payment request');
  }
};
```

### 2. Mark Payment as Cash

**Use Case:** Member paid cash directly to admin

```typescript
const handleMarkAsCash = async (paymentId: number) => {
  try {
    await apiClient.post(`/payments/${paymentId}/mark-paid`, {
      payment_type: 'cash'
    });
    
    alert('Payment marked as cash received');
  } catch (error) {
    alert('Failed to mark payment');
  }
};
```

### 3. View All Unpaid Members

Add to dashboard:

```typescript
const unpaidMembers = members.filter(m => !m.paid_current_round);

{unpaidMembers.length > 0 && isAdmin && (
  <Card>
    <h3>Unpaid Members ({unpaidMembers.length})</h3>
    <div className="unpaid-members-list">
      {unpaidMembers.map(member => (
        <div key={member.user_id} className="unpaid-member-item">
          <span>{member.name}</span>
          <PaymentButton
            groupId={group.id}
            userId={member.user_id}
            roundNumber={group.current_round}
            amount={group.contribution_amount}
            isAdmin={true}
            onSuccess={loadDashboard}
          />
        </div>
      ))}
    </div>
  </Card>
)}
```

---

## Troubleshooting

### Issue 1: "Failed to obtain MTN MoMo token"

**Cause:** Invalid credentials

**Solution:**
```bash
# Re-run setup
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py

# Or manually check credentials
python3 << EOF
from app.integrations.mtn_momo_integration import mtn_momo_service
try:
    token = mtn_momo_service._get_auth_token()
    print("✅ Credentials valid")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

### Issue 2: "Payment request failed"

**Possible causes:**
1. Invalid phone number format
2. Insufficient sandbox balance
3. Network error

**Check:**
```bash
# View logs
docker logs sususave_backend | grep -i "momo\|payment"

# Test directly
curl -X POST http://localhost:8000/payments/admin/request-payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "group_id": 1,
    "user_id": 2,
    "round_number": 1
  }'
```

### Issue 3: "Callback URL not accessible"

**Cause:** ngrok not running or URL not registered

**Solution:**
```bash
# Start ngrok
ngrok http 8000

# Update .env with new URL
MTN_CALLBACK_URL=https://new-ngrok-url.ngrok-free.app/ussd/callback

# Restart backend
docker-compose restart backend
```

### Issue 4: Phone number format errors

**Fix phone number formatting:**
```python
# MTN expects: 233XXXXXXXXX (no +, no spaces)

# Good: 233244123456
# Bad:  +233244123456
# Bad:  233 24 412 3456
# Bad:  0244123456
```

---

## Next Steps

1. **Test Sandbox:**
   - Run setup script
   - Test with test numbers
   - Verify payment flow

2. **Implement Frontend:**
   - Add PaymentButton component
   - Update GroupDashboardPage
   - Test user and admin flows

3. **Go to Production:**
   - Get production subscription key
   - Create production API credentials
   - Update environment to production
   - Test with real money (small amounts first!)

---

## Resources

- **MTN MoMo Portal**: https://momodeveloper.mtn.com/
- **API Documentation**: https://momodeveloper.mtn.com/api-documentation/
- **Setup Script**: `/Users/maham/susu/backend/setup_mtn_momo.py`
- **Integration Code**: `/Users/maham/susu/backend/app/integrations/mtn_momo_integration.py`

---

**Last Updated**: October 23, 2025  
**Status**: Ready for Implementation  
**Time to Setup**: 15 minutes

