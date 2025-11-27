# Cash Payment & Freemium Model Implementation

## Overview

This implementation adds manual payment triggers, cash payment support, and a freemium model that allows full app functionality without mobile money integration. This makes the app truly open-source and accessible for communities that prefer cash-based savings groups.

## Features Implemented

### 1. **Manual Payment Triggers**
- Members can view their unpaid payment for the current round
- "Pay Now" button allows manual payment initiation
- Works for MOMO-enabled groups (triggers mobile money payment)
- Provides helpful error messages for cash-only groups

### 2. **Cash Payment Marking**
- Group admins can mark payments as "paid" when receiving cash
- Creates audit trail with admin who marked the payment
- Sends SMS confirmation to member
- Generates unique CASH transaction IDs (format: `CASH-{timestamp}-{payment_id}`)

### 3. **Cash-Only Groups (Freemium Model)**
- Groups can be designated as "cash-only" during creation
- No mobile money integration required
- All payments must be marked manually by admins
- Enables full app functionality for open-source use without payment gateway accounts

### 4. **Admin Role Management**
- Group creators can assign/revoke admin roles to members
- Admins can mark payments as paid
- Creator's admin status is protected (cannot be removed)
- SMS notifications when admin roles change

## Database Changes

### New Fields

**payments table:**
- `payment_type` (enum: 'momo', 'cash') - How payment was made
- `marked_paid_by` (foreign key to users) - Admin who marked cash payment

**groups table:**
- `cash_only` (boolean) - If true, group uses cash payments only

### Migration

Run migration to add new columns:
```bash
cd backend
alembic upgrade head
```

Migration file: `backend/alembic/versions/20251022_add_cash_payments.py`

## API Endpoints

### Payment Endpoints

#### Get Unpaid Payment
```http
GET /groups/{group_id}/unpaid-payment
Authorization: Bearer <token>
```

**Response:**
```json
{
  "payment_id": 123,
  "group_id": 1,
  "group_name": "Weekly Savings",
  "round_number": 3,
  "amount": 50.0,
  "is_paid": false,
  "is_cash_only": true
}
```

#### Pay Now (Manual Payment)
```http
POST /payments/{payment_id}/pay-now
Authorization: Bearer <token>
```

Triggers MOMO payment for MOMO groups, returns error for cash-only groups.

#### Mark Payment as Paid (Admin Only)
```http
POST /payments/{payment_id}/mark-paid
Authorization: Bearer <token>
Content-Type: application/json

{
  "note": "Received cash at meeting"  // optional
}
```

**Response:**
```json
{
  "id": 123,
  "transaction_id": "CASH-1698765432-123",
  "user_id": 5,
  "group_id": 1,
  "round_number": 3,
  "amount": 50.0,
  "payment_date": "2024-10-22T14:30:00",
  "status": "success",
  "payment_type": "cash",
  "marked_paid_by": 1,
  "retry_count": 0,
  "created_at": "2024-10-22T14:00:00"
}
```

### Group Endpoints

#### Set Member Admin (Creator Only)
```http
POST /groups/{group_id}/members/{user_id}/set-admin
Authorization: Bearer <token>
Content-Type: application/json

{
  "is_admin": true
}
```

**Response:**
```json
{
  "id": 10,
  "user_id": 5,
  "group_id": 1,
  "rotation_position": 2,
  "is_admin": true,
  "is_active": true,
  "join_date": "2024-10-20T10:00:00"
}
```

## Mobile App Changes

### CreateGroupScreen

- Added "Cash Only Group" toggle switch
- Visual indicator showing payment method in preview
- Toggle explanation text updates dynamically

### GroupDashboardScreen (TODO)

**For all members:**
- Unpaid payment card showing current round payment status
- "Pay Now" button (or cash payment message)

**For admins:**
- List of unpaid members for current round
- "Mark as Paid" button for each unpaid member
- Confirmation dialog before marking

**For creators:**
- "Make Admin" / "Remove Admin" buttons on member list
- Confirmation dialog before role changes

### API Service Files

**paymentService.ts:**
- `getUnpaidPayment(groupId)` - Get unpaid payment for user
- `payNow(paymentId)` - Trigger manual payment
- `markAsPaid(paymentId)` - Admin marks cash payment

**groupService.ts:**
- `setMemberAdmin(groupId, userId, isAdmin)` - Assign/revoke admin role
- Updated `createGroup()` to include `cash_only` field

## Testing

### Backend Tests

**test_cash_payments.py:**
```bash
cd backend
python test_cash_payments.py
```

Tests:
- ✅ Cash-only group creation
- ✅ MOMO skip in cash-only groups
- ✅ Admin marking payment as paid
- ✅ Non-admin permissions blocking

**test_admin_assignment.py:**
```bash
cd backend
python test_admin_assignment.py
```

Tests:
- ✅ Creator assigns admin role
- ✅ Creator revokes admin role
- ✅ Non-creator cannot assign admin
- ✅ Creator's admin status protected

## Usage Examples

### Creating a Cash-Only Group

**Mobile App:**
1. Navigate to Create Group screen
2. Enter group details (name, amount, members)
3. Toggle "Cash Only Group" switch ON
4. Create group

**API:**
```python
POST /groups
{
  "name": "Community Savings",
  "contribution_amount": 100.0,
  "num_cycles": 10,
  "cash_only": true
}
```

### Admin Marking Payment as Paid

1. Admin receives cash from member
2. Opens group dashboard in app
3. Finds member in "Unpaid Members" list
4. Clicks "Mark as Paid"
5. Confirms action
6. Member receives SMS confirmation

### Assigning Admin Role

1. Group creator opens member list
2. Clicks "Make Admin" next to member name
3. Confirms action
4. Member receives SMS notification about new role
5. Member can now mark payments as paid

## Freemium Model Benefits

### For Open-Source Use
- ✅ No payment gateway accounts needed
- ✅ No MTN MOMO API keys required
- ✅ Works completely offline for payment collection
- ✅ Self-hosted deployments fully functional

### For Communities
- ✅ Familiar cash-based system
- ✅ Lower barriers to adoption
- ✅ Gradual transition to digital payments possible
- ✅ Hybrid groups can use both cash and MOMO

### Upgrade Path
Groups can start as cash-only and later:
1. Integrate MTN MOMO when ready
2. Create new MOMO-enabled groups
3. Existing members familiar with app workflow

## Security Considerations

### Permissions
- Only group creator can assign/revoke admin roles
- Only admins (or creator) can mark payments as paid
- Users can only trigger payments for themselves
- All actions are audit-logged

### Audit Trail
- Cash payments record which admin marked them paid
- Transaction IDs uniquely identify cash payments
- Timestamps recorded for all actions
- SMS notifications sent for verification

## Configuration

### Environment Variables

No additional environment variables needed for cash-only groups. To enable MOMO alongside cash:

```env
# Optional - for MOMO-enabled groups
MTN_MOMO_ENABLED=true
MTN_MOMO_SUBSCRIPTION_KEY=your_key
MTN_MOMO_USER_ID=your_user_id
MTN_MOMO_API_KEY=your_api_key
```

## Next Steps

### Mobile UI Completion
The following UI components still need to be implemented in GroupDashboardScreen:

1. **UnpaidPaymentCard** component
2. **AdminPaymentActions** component (list of unpaid members)
3. Admin role management UI in member list

### Web App (Optional)
Similar updates can be made to the web dashboard if needed.

## Summary

This implementation enables:
- ✅ Full app functionality without payment gateway
- ✅ Manual payment tracking for cash-based groups
- ✅ Admin role management by group creators
- ✅ Hybrid cash/MOMO support in single deployment
- ✅ Open-source friendly with no required integrations
- ✅ Comprehensive audit trail and permissions

The app is now truly freemium - communities can use it fully for free with cash payments, and optionally upgrade to automated MOMO payments when ready.

