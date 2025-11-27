# Group Invitation - Quick Start Guide

## 🚀 Setup

### 1. Run Database Migration
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

This creates the `group_invitations` table.

### 2. Test the Implementation
```bash
cd backend
python test_invitation_feature.py
```

## 📱 Usage Examples

### For Mobile App (React Native)

```typescript
// screens/GroupDetailsScreen.tsx

import { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import api from '../api/client';

export const InviteMemberSection = ({ groupId }: { groupId: number }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const inviteMember = async () => {
    if (!phoneNumber.startsWith('+')) {
      Alert.alert('Error', 'Phone number must include country code (e.g., +233...)');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/groups/${groupId}/invite`, {
        phone_number: phoneNumber
      });
      Alert.alert('Success', 'Invitation sent!');
      setPhoneNumber('');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <TextInput
        placeholder="+233201234567"
        value={phoneNumber}
        onChangeText={setPhoneNumber}
        keyboardType="phone-pad"
      />
      <Button 
        title="Invite Member" 
        onPress={inviteMember}
        disabled={loading}
      />
    </View>
  );
};

// Show pending invitations
export const PendingInvitations = ({ groupId }: { groupId: number }) => {
  const [invitations, setInvitations] = useState([]);

  useEffect(() => {
    loadInvitations();
  }, [groupId]);

  const loadInvitations = async () => {
    try {
      const response = await api.get(`/groups/${groupId}/invitations`);
      setInvitations(response.data);
    } catch (error) {
      console.error('Failed to load invitations:', error);
    }
  };

  return (
    <View>
      {invitations.map(inv => (
        <View key={inv.id}>
          <Text>{inv.phone_number}</Text>
          <Text>Invited by: {inv.invited_by_name}</Text>
          <Text>Status: {inv.status}</Text>
        </View>
      ))}
    </View>
  );
};
```

### For USSD Integration

The join flow already handles invitations automatically:

```python
# In your USSD service
def handle_join_group(session_id: str, phone_number: str, text: str):
    # User enters group code
    group_code = text.split('*')[-1]
    
    # When user joins, invitation is auto-accepted
    user = get_user_by_phone(phone_number)
    membership = GroupService.join_group(db, group_code, user)
    
    # If there was a pending invitation, it's now accepted
    return f"END Welcome to the group! Position: {membership.rotation_position}"
```

## 🔑 API Quick Reference

### Admin Actions

**Invite Member**
```bash
curl -X POST http://localhost:8000/groups/1/invite \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+233201234567"}'
```

**List Pending Invitations**
```bash
curl http://localhost:8000/groups/1/invitations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### User Actions

**Accept Invitation (Explicit)**
```bash
curl -X POST http://localhost:8000/groups/invitations/1/accept \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Join Group (Auto-accepts invitation)**
```bash
curl -X POST http://localhost:8000/groups/join \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"group_code": "ABC123"}'
```

## 📧 SMS Messages

The system sends different messages based on user status:

### For Registered Users
```
You've been invited by John Doe to join Village Savings. 
Dial *920*55# or use the app with code: ABC123 to accept.
```

### For Unregistered Users
```
You've been invited to join Village Savings susu group! 
Register via USSD (*920*55#) or download the app, then use code: ABC123 to join.
```

## 🔒 Permissions

| Action | Required Permission |
|--------|-------------------|
| Invite member | Group admin |
| Accept invitation | Match phone number |
| View invitations | Group admin |
| Join group | Any authenticated user |

## 💡 Common Scenarios

### Scenario 1: Invite Registered User
1. Admin clicks "Invite Member"
2. Enters phone number: `+233201234567`
3. System sends SMS with group code
4. User receives SMS and joins via app/USSD
5. Invitation automatically accepted

### Scenario 2: Invite Unregistered User
1. Admin clicks "Invite Member"
2. Enters phone number: `+233209999999`
3. System sends SMS with registration instructions
4. User registers via USSD or app
5. User joins group with code from SMS
6. Invitation automatically accepted

### Scenario 3: Check Invitation Status
1. Admin opens group details
2. Views "Pending Invitations" section
3. Sees list of phone numbers waiting to join
4. Can track who was invited and when

## ⚠️ Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Only group admins can invite members" | User is not admin | Make user admin first |
| "User is already a member of this group" | Phone already in group | No action needed |
| "There is already a pending invitation..." | Duplicate invitation | Wait for acceptance or cancel existing |
| "Group not found" | Invalid group ID | Check group ID |
| "This invitation is not for your phone number" | Phone mismatch | User must register with invited number |

## 🧪 Testing Checklist

- [ ] Admin can invite member
- [ ] Non-admin cannot invite member
- [ ] SMS is sent on invitation
- [ ] Registered user receives personalized SMS
- [ ] Unregistered user receives registration SMS
- [ ] User can join via group code
- [ ] Invitation auto-accepts on join
- [ ] Cannot invite existing member
- [ ] Cannot create duplicate pending invitation
- [ ] Pending invitations list updates correctly
- [ ] Audit logs track invitation actions

## 📊 Database Schema

```sql
CREATE TABLE group_invitations (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id),
    phone_number VARCHAR NOT NULL,  -- encrypted
    invited_by INTEGER REFERENCES users(id),
    status VARCHAR NOT NULL,  -- pending, accepted, rejected, expired
    created_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP
);

CREATE INDEX ON group_invitations(group_id);
CREATE INDEX ON group_invitations(phone_number);
CREATE INDEX ON group_invitations(status);
```

## 🔍 Troubleshooting

### SMS Not Sending
- Check `backend/sms_logs.txt` for mock messages
- Verify phone number format includes country code
- Check SMS integration settings in `.env`

### Invitation Not Auto-Accepting
- Verify phone numbers match exactly
- Check invitation status in database
- Review audit logs for join event

### Permission Errors
- Confirm user is group admin
- Check membership is_admin field
- Verify user is authenticated

## 📚 Related Documentation

- [Full Feature Documentation](GROUP_INVITATION_FEATURE.md)
- [API Documentation](docs/API.md)
- [SMS Integration](AFRICASTALKING_INTEGRATION_SUMMARY.md)
- [Database Models](backend/app/models/)

## 🆘 Support

If you encounter issues:
1. Check SMS logs: `backend/sms_logs.txt`
2. Check audit logs in database
3. Run test script: `python test_invitation_feature.py`
4. Review error messages in API response

