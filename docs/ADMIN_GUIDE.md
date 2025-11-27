# SusuSave Admin Portal User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [User Management](#user-management)
4. [Group Management](#group-management)
5. [Payment Management](#payment-management)
6. [Payout Management](#payout-management)
7. [Invitations](#invitations)
8. [System Settings](#system-settings)
9. [Audit Logs](#audit-logs)
10. [Admin Management](#admin-management)

## Getting Started

### Login

1. Navigate to the admin portal (usually http://localhost:3001)
2. Enter your admin phone number (with country code)
3. Enter your password
4. Click "Login"

### Navigation

The sidebar on the left provides quick access to all admin functions:
- 📊 Dashboard - Overview and statistics
- 👥 Users - User management
- 👪 Groups - Group management
- 💳 Payments - Payment transactions
- 💰 Payouts - Payout approvals
- ✉️ Invitations - Group invitations
- ⚙️ Settings - System configuration
- 📝 Audit Logs - Activity tracking

## Dashboard

The dashboard provides a quick overview of your system:

### Key Metrics
- **Total Users**: Number of registered users
- **Active Users**: Users who have made payments in the last 30 days
- **Total Groups**: All groups in the system
- **Active Groups**: Groups currently running
- **Total Revenue**: All-time revenue from successful payments
- **Pending Actions**: Payments and payouts requiring attention

### Quick Actions
Click any quick action button to navigate to that section.

### Recent Activity
View the latest system activities including:
- New user registrations
- Group creations
- Payment transactions

## User Management

### View All Users

Navigate to **Users** to see all registered users.

**Features:**
- Search by name
- Filter by user type (App/USSD)
- Filter by KYC status
- Export to CSV

### User Details

Click "View" on any user to see:
- Personal information
- KYC status
- Group memberships
- Payment history
- Total contributions

### User Actions

#### Edit User Information
1. Click "View" on a user
2. Click "Edit Information"
3. Update name or email
4. Click "Save"

#### Verify KYC Manually
1. Go to user details
2. Click "Verify KYC" (if not already verified)
3. Confirm the action

#### Deactivate User
1. Go to user details
2. Click "Deactivate User"
3. Confirm (this removes them from all groups)

#### Reset Password
Super admins can reset user passwords:
1. Go to user details
2. Click "Reset Password"
3. Enter new password
4. Confirm

## Group Management

### View All Groups

Navigate to **Groups** to see all ROSCA groups.

**Information Displayed:**
- Group code and name
- Contribution amount
- Current status
- Number of members
- Total contributions

### Group Details

Click "View" on any group to see:
- Group information
- Member list with rotation positions
- Payment summary
- Group status

### Group Actions

#### Suspend Group
1. Go to group details
2. Click "Suspend Group"
3. Confirm (prevents new payments and activities)

#### Reactivate Group
1. Find suspended group
2. Click "Reactivate"
3. Group becomes active again

#### Remove Member
1. Go to group details
2. Find member in list
3. Click "Remove"
4. Confirm

#### Delete Group (Super Admin Only)
⚠️ Permanent action - use with caution
1. Go to group details
2. Click "Delete Group"
3. Confirm deletion

## Payment Management

### View Payments

Navigate to **Payments** to see all payment transactions.

**Filter Options:**
- Payment status (pending, success, failed)
- Payment type (MoMo, Cash)
- Date range
- Export to CSV

### Payment Details

Click on any payment to view:
- User information
- Group information
- Payment amount and status
- Transaction ID
- Retry count (for failed payments)

### Update Payment Status

1. Find the payment
2. Click "Update Status"
3. Select new status
4. Confirm

**Status Options:**
- Pending
- Success
- Failed

### Review Failed Payments

1. Filter by "Failed" status
2. Review error details
3. Retry or mark as resolved
4. Contact user if needed

## Payout Management

### View Payouts

Navigate to **Payouts** to see all payout requests.

### Approve Payout

1. Find pending payout
2. Click "Approve"
3. Confirm (processes payment to recipient)

### Reject Payout

1. Find pending payout
2. Click "Reject"
3. Enter rejection reason
4. Confirm

**Note:** Payouts are typically generated automatically when it's a member's turn to receive the pool.

## Invitations

### View Invitations

Navigate to **Invitations** to see all group invitations.

**Information:**
- Group name
- Invited phone number
- Who sent the invitation
- Status (pending, accepted, rejected, expired)
- Date created

### Manage Invitations

#### Expire Invitation
1. Find pending invitation
2. Click "Expire"
3. Invitation becomes invalid

#### Delete Invitation
1. Find invitation
2. Click "Delete"
3. Permanently removes invitation record

## System Settings

### View Settings

Navigate to **Settings** to manage system configuration.

**Categories:**
- SMS Configuration
- Payment Gateway Settings
- Feature Toggles
- System Parameters

### Update Setting (Super Admin Only)

1. Find the setting
2. Click "Edit"
3. Enter new value
4. Click "Save"

### Create Setting (Super Admin Only)

1. Click "Create New Setting"
2. Enter:
   - Setting key (unique identifier)
   - Setting value
   - Category
   - Description (optional)
3. Click "Create"

## Audit Logs

### View Audit Logs

Navigate to **Audit Logs** to see all administrative actions.

**Filter Options:**
- Entity type (user, group, payment, etc.)
- Action (create, update, delete, approve, etc.)
- Performed by (admin ID)
- Date range

### Audit Log Information

Each log entry shows:
- Entity type and ID
- Action performed
- Admin who performed it
- Timestamp
- Details/description

**Use Cases:**
- Track changes to critical data
- Investigate suspicious activity
- Compliance and reporting
- Troubleshooting issues

## Admin Management

**Note:** Only available to Super Admins

### View Admins

Navigate to **Settings → Admin Management** to see all admin users.

### Create New Admin

1. Click "Create Admin"
2. Enter:
   - Name
   - Phone number
   - Password
   - Admin role (super_admin, finance_admin, support_admin)
3. Click "Create"

### Update Admin Role

1. Find admin user
2. Click "Edit Role"
3. Select new role
4. Confirm

### Revoke Admin Access

1. Find admin user
2. Click "Revoke Access"
3. Confirm (converts to regular user)

**Note:** You cannot revoke your own admin access.

## Data Export

### Export Users

1. Go to Users page
2. Click "Export CSV"
3. File downloads automatically

Includes:
- User ID, name, phone, email
- User type, KYC status
- Admin status and role
- Created date

### Export Payments

1. Go to Payments page
2. Optionally set date filters
3. Click "Export CSV"
4. File downloads automatically

Includes:
- Payment ID, transaction ID
- User and group information
- Amount, status, type
- Payment dates

## Best Practices

### Security
- Never share your admin credentials
- Log out when finished
- Use strong passwords
- Review audit logs regularly

### User Management
- Verify KYC before approving large transactions
- Investigate suspicious user activity
- Respond promptly to user issues

### Financial Management
- Review pending payouts daily
- Investigate failed payments
- Monitor total revenue trends
- Export financial reports monthly

### System Maintenance
- Check dashboard daily for anomalies
- Review error logs weekly
- Update settings as needed
- Backup data regularly

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Quick search (future feature)
- `Escape` - Close modals
- `Enter` - Submit forms

## Troubleshooting

### Can't Login
- Verify phone number format includes country code
- Check password (case-sensitive)
- Contact super admin if locked out

### Data Not Loading
- Check internet connection
- Refresh the page
- Clear browser cache
- Check backend server status

### Permission Denied
- Verify your admin role
- Some actions require super admin
- Contact super admin for role upgrade

## Support

For technical issues:
1. Check audit logs for errors
2. Note the exact error message
3. Check browser console (F12)
4. Contact system administrator with details

## Updates

This admin portal is continuously updated. Check for:
- New features announcements
- Security updates
- Performance improvements
- Bug fixes

Last updated: October 2025
Version: 1.0.0

