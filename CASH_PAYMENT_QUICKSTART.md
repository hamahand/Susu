# Cash Payment & Admin Features - Quick Start Guide

## 🚀 Quick Setup

### 1. Run Database Migration
```bash
cd backend
alembic upgrade head
```

This adds:
- `payment_type` column to payments
- `marked_paid_by` column to payments
- `cash_only` column to groups

### 2. Test Backend
```bash
# Test cash payments
python test_cash_payments.py

# Test admin assignment
python test_admin_assignment.py
```

### 3. Start Backend Server
```bash
cd backend
./run.sh
```

## 📱 Using the Features

### Create a Cash-Only Group

**Mobile App:**
1. Go to "Create Group"
2. Fill in group details
3. Toggle "Cash Only Group" ON
4. Click "Create Group"

**API:**
```bash
curl -X POST http://localhost:8000/groups \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cash Savings Circle",
    "contribution_amount": 50.0,
    "num_cycles": 5,
    "cash_only": true
  }'
```

### Check Unpaid Payment

```bash
curl http://localhost:8000/groups/1/unpaid-payment \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "payment_id": 10,
  "group_id": 1,
  "group_name": "Cash Savings Circle",
  "round_number": 2,
  "amount": 50.0,
  "is_paid": false,
  "is_cash_only": true
}
```

### Mark Payment as Paid (Admin)

```bash
curl -X POST http://localhost:8000/payments/10/mark-paid \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Assign Admin Role (Creator Only)

```bash
curl -X POST http://localhost:8000/groups/1/members/5/set-admin \
  -H "Authorization: Bearer CREATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_admin": true}'
```

## 🔑 Key Concepts

### Payment Types
- **MOMO**: Mobile money payment (automated)
- **CASH**: Cash payment (manually marked by admin)

### Group Types
- **Regular Groups**: Use mobile money (MOMO)
- **Cash-Only Groups**: Only cash payments (freemium)

### User Roles
- **Creator**: Creates group, always admin, can assign other admins
- **Admin**: Can mark payments as paid, view invitations
- **Member**: Can pay contributions, view dashboard

## 📊 Permission Matrix

| Action | Creator | Admin | Member |
|--------|---------|-------|--------|
| Mark payment as paid | ✅ | ✅ | ❌ |
| Assign admin role | ✅ | ❌ | ❌ |
| Trigger own payment | ✅ | ✅ | ✅ |
| View group dashboard | ✅ | ✅ | ✅ |
| Invite members | ✅ | ✅ | ❌ |

## 💡 Common Use Cases

### Scenario 1: Weekly Cash Meeting
1. Create cash-only group
2. Members meet weekly
3. Members pay cash to treasurer
4. Treasurer (admin) marks each payment in app
5. Members get SMS confirmation

### Scenario 2: Hybrid Group
1. Create regular (MOMO) group
2. Member doesn't have mobile money
3. Member pays cash to admin
4. Admin creates pending payment in system
5. Admin marks it as cash paid
6. Everyone sees member as paid

### Scenario 3: Multiple Admins
1. Creator assigns trusted members as admins
2. Multiple people can collect and mark payments
3. Audit trail shows who marked each payment
4. Creator can revoke admin role anytime

## 🛠️ Troubleshooting

### "Only group admins can mark payments as paid"
- Check user is admin in group
- Check group creator status
- Verify membership is active

### "This is a cash-only group"
- Trying to use MOMO in cash-only group
- Either create new MOMO group or pay cash to admin

### "Only the group creator can assign admin roles"
- Only creator can assign/revoke admin
- Even current admins cannot assign others
- Contact group creator to request admin role

## 📝 Code Examples

### Get Unpaid Members (Admin View)

```python
from app.models import Payment, PaymentStatus, Group
from sqlalchemy import and_

def get_unpaid_members(db, group_id, round_number):
    """Get members who haven't paid for current round."""
    unpaid = db.query(Payment).filter(
        and_(
            Payment.group_id == group_id,
            Payment.round_number == round_number,
            Payment.status != PaymentStatus.SUCCESS
        )
    ).all()
    return unpaid
```

### Check if User is Admin

```python
from app.models import Membership, Group

def is_user_admin(db, user_id, group_id):
    """Check if user is admin or creator of group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group.creator_id == user_id:
        return True
    
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.group_id == group_id,
        Membership.is_active == True
    ).first()
    
    return membership and membership.is_admin
```

## 🎯 Testing Checklist

- [ ] Create cash-only group
- [ ] Create regular MOMO group
- [ ] Try MOMO payment in cash-only (should fail)
- [ ] Mark payment as paid (admin)
- [ ] Try marking payment as non-admin (should fail)
- [ ] Assign admin role (creator)
- [ ] Try assigning admin as non-creator (should fail)
- [ ] Revoke admin role
- [ ] Check SMS notifications sent

## 📚 Related Documentation

- **Full Implementation Guide**: `CASH_PAYMENT_FREEMIUM_COMPLETE.md`
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **API Documentation**: `docs/API.md`
- **Backend Tests**: `test_cash_payments.py`, `test_admin_assignment.py`

## 🆘 Support

For issues or questions:
1. Check implementation status document
2. Review test files for examples
3. Check API documentation
4. Review audit logs in database

---

**Feature Status**: ✅ Backend Complete | 🚧 Mobile UI In Progress

