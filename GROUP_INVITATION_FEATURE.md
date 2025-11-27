# Group Member Invitation Feature

## Overview
Group admins can now invite new members to their susu groups by phone number. The system sends SMS invitations with the group code, tracks invitation status, and automatically links invitations when users join.

## Features Implemented

### 1. Database Schema
- **New Table**: `group_invitations`
  - Tracks all invitations sent
  - Stores encrypted phone numbers
  - Maintains invitation status (pending, accepted, rejected, expired)
  - Links to group and inviter

### 2. Invitation Workflow

#### For Admins
1. Admin sends invitation with phone number
2. System checks:
   - Inviter is an admin of the group
   - Phone number is not already a member
   - No pending invitation exists for that phone number
3. Creates invitation record
4. Sends appropriate SMS based on user registration status

#### For Invitees
Two paths:

**Existing Users:**
- Receive SMS: "You've been invited by [Name] to join [Group]. Dial *920*55# or use the app with code: [CODE] to accept."
- Can join using group code via USSD or app
- Invitation automatically accepted when they join

**New Users:**
- Receive SMS: "You've been invited to join [Group] susu group! Register via USSD (*920*55#) or download the app, then use code: [CODE] to join."
- Must register first
- Then join using the group code
- Invitation automatically accepted when they join

### 3. API Endpoints

#### Invite Member
```http
POST /groups/{group_id}/invite
Authorization: Bearer <token>
Content-Type: application/json

{
  "phone_number": "+233201234567"
}

Response: 201 Created
{
  "id": 1,
  "group_id": 5,
  "group_name": "Village Savings",
  "phone_number": "+233201234567",
  "status": "pending",
  "invited_by_name": "John Doe",
  "created_at": "2025-10-22T10:30:00",
  "accepted_at": null
}
```

**Requirements:**
- User must be authenticated
- User must be an admin of the group
- Phone number must include country code
- Phone number cannot already be a member

**Errors:**
- 403: Not a group admin
- 404: Group not found
- 400: User already a member
- 400: Pending invitation already exists

#### Accept Invitation
```http
POST /groups/invitations/{invitation_id}/accept
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Successfully accepted invitation",
  "group_id": 5,
  "rotation_position": 4
}
```

**Requirements:**
- User must be authenticated
- Invitation must exist and be pending
- User's phone number must match invitation

**Errors:**
- 404: Invitation not found
- 400: Invitation already processed
- 403: Phone number doesn't match

#### Get Pending Invitations
```http
GET /groups/{group_id}/invitations
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "group_id": 5,
    "group_name": "Village Savings",
    "phone_number": "+233201234567",
    "status": "pending",
    "invited_by_name": "John Doe",
    "created_at": "2025-10-22T10:30:00",
    "accepted_at": null
  }
]
```

**Requirements:**
- User must be authenticated
- User must be an admin of the group

**Errors:**
- 403: Not a group admin

### 4. Auto-Accept on Join
When a user joins a group using a group code (via `/groups/join` endpoint):
1. System checks for pending invitation matching user's phone number
2. If found, automatically marks invitation as accepted
3. Links membership to invitation in audit log
4. User receives welcome SMS

### 5. SMS Templates

#### Existing User Invitation
```
You've been invited by [Inviter Name] to join [Group Name]. 
Dial *920*55# or use the app with code: [GROUP_CODE] to accept.
```

#### New User Invitation
```
You've been invited to join [Group Name] susu group! 
Register via USSD (*920*55#) or download the app, then use code: [GROUP_CODE] to join.
```

### 6. Audit Trail
All invitation actions are logged:
- Invitation sent (entity: invitation, action: invite)
- Invitation accepted (entity: membership, action: accept_invitation)
- Auto-accept on join (entity: membership, action: join, includes invitation_id)

## Database Migration

To apply the new schema:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

This will create the `group_invitations` table with all necessary indexes.

## Security Features

1. **Phone Number Encryption**: All phone numbers in invitations are encrypted using Fernet encryption
2. **Admin-Only Access**: Only group admins can send invitations
3. **Phone Number Verification**: System verifies invitee's phone matches invitation
4. **Duplicate Prevention**: Cannot send multiple pending invitations to same number
5. **Member Check**: Cannot invite existing members

## Testing

### Manual Testing Steps

1. **Create a test group** (as admin user)
2. **Invite a new member**:
   ```bash
   curl -X POST http://localhost:8000/groups/1/invite \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+233201234567"}'
   ```

3. **Check SMS logs**: `backend/sms_logs.txt`

4. **List pending invitations**:
   ```bash
   curl http://localhost:8000/groups/1/invitations \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

5. **Join group as invitee**:
   ```bash
   curl -X POST http://localhost:8000/groups/join \
     -H "Authorization: Bearer INVITEE_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"group_code": "ABC123"}'
   ```

6. **Verify invitation accepted**: Check invitations list again

### Integration Testing

Example test case:

```python
def test_invite_and_join_flow():
    # Admin invites user
    response = client.post(
        f"/groups/{group_id}/invite",
        json={"phone_number": "+233201234567"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    invitation = response.json()
    assert invitation["status"] == "pending"
    
    # Invitee joins group
    response = client.post(
        "/groups/join",
        json={"group_code": group_code},
        headers={"Authorization": f"Bearer {invitee_token}"}
    )
    assert response.status_code == 200
    
    # Check invitation is accepted
    response = client.get(
        f"/groups/{group_id}/invitations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0  # No pending invitations
```

## Mobile App Integration

### React Native Example

```typescript
// Invite a member
const inviteMember = async (groupId: number, phoneNumber: string) => {
  try {
    const response = await api.post(`/groups/${groupId}/invite`, {
      phone_number: phoneNumber
    });
    Alert.alert('Success', 'Invitation sent!');
    return response.data;
  } catch (error) {
    Alert.alert('Error', error.response?.data?.detail || 'Failed to send invitation');
  }
};

// Accept invitation
const acceptInvitation = async (invitationId: number) => {
  try {
    const response = await api.post(`/groups/invitations/${invitationId}/accept`);
    Alert.alert('Success', 'You joined the group!');
    return response.data;
  } catch (error) {
    Alert.alert('Error', error.response?.data?.detail || 'Failed to accept invitation');
  }
};

// List pending invitations (admin only)
const getPendingInvitations = async (groupId: number) => {
  try {
    const response = await api.get(`/groups/${groupId}/invitations`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch invitations:', error);
    return [];
  }
};
```

## Future Enhancements

1. **Invitation Expiry**: Add automatic expiration after X days
2. **Reject Invitation**: Allow users to explicitly reject invitations
3. **Resend Invitation**: Allow admins to resend SMS
4. **Invitation Limits**: Rate limiting per group/user
5. **Batch Invitations**: Invite multiple users at once
6. **Email Invitations**: Support email in addition to SMS
7. **Custom Messages**: Allow admins to add personal message to invitation

## Files Modified/Created

### New Files
- `backend/app/models/invitation.py` - GroupInvitation model
- `backend/alembic/versions/20251022_create_invitations_table.py` - Database migration
- `GROUP_INVITATION_FEATURE.md` - This documentation

### Modified Files
- `backend/app/schemas/group_schema.py` - Added invitation schemas
- `backend/app/services/group_service.py` - Added invitation methods
- `backend/app/routers/groups.py` - Added invitation endpoints
- `backend/app/integrations/sms_sender.py` - Added invitation SMS templates
- `backend/app/models/__init__.py` - Exported GroupInvitation
- `backend/app/schemas/__init__.py` - Exported invitation schemas

## Support

For issues or questions about the invitation feature, please check:
1. SMS logs: `backend/sms_logs.txt`
2. Database audit logs: `audit_logs` table
3. API error responses for detailed error messages

