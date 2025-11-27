# Admin CRM - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Run Migration
```bash
cd backend
alembic upgrade head
```

### Step 2: Create Super Admin
```bash
python create_super_admin.py
```
Follow the prompts and enter:
- Name: Your Name
- Phone: +233XXXXXXXXX
- Password: (min 6 chars)

### Step 3: Start Admin Portal
```bash
cd web/admin
npm install
npm run dev
```

### Step 4: Login
Open **http://localhost:3001** and login with your credentials.

## 📋 Quick Reference

### Admin Roles
- **SUPER_ADMIN**: Full access (create admins, delete groups, system settings)
- **FINANCE_ADMIN**: Financial management (approve payouts, manage payments)
- **SUPPORT_ADMIN**: User support (manage users, verify KYC)

### Key Features
- **Dashboard**: Overview stats and recent activity
- **Users**: Search, filter, edit, verify KYC, export CSV
- **Groups**: View, suspend, reactivate, remove members
- **Payments**: Filter, update status, view failed payments
- **Payouts**: Approve/reject pending payouts
- **Audit Logs**: Track all admin actions
- **Settings**: System configuration (super admin only)

### API Endpoints
Backend running on: **http://localhost:8000**
- Dashboard: `/admin/dashboard/stats`
- Users: `/admin/users`
- Groups: `/admin/groups`
- Payments: `/admin/payments`
- Full docs: http://localhost:8000/docs

### Common Tasks

**Verify User KYC:**
1. Users → Find user → View
2. Click "Verify KYC"

**Approve Payout:**
1. Payouts → Find pending
2. Click "Approve"

**Suspend Group:**
1. Groups → Find group → View
2. Click "Suspend Group"

**Export Data:**
1. Go to Users or Payments
2. Click "Export CSV"

**Create New Admin:** (Super Admin only)
1. Settings → Admin Management
2. Create Admin
3. Fill form and submit

## 🔧 Troubleshooting

**Can't login?**
- Check phone format: +233XXXXXXXXX
- Verify password is correct
- Run `python create_super_admin.py` again

**Frontend won't start?**
```bash
cd web/admin
rm -rf node_modules
npm install
npm run dev
```

**API not connecting?**
- Check backend is running on port 8000
- Check vite.config.ts proxy settings

## 📖 Documentation

- **Setup Guide**: `backend/docs/ADMIN_SETUP.md`
- **User Guide**: `docs/ADMIN_GUIDE.md`
- **Complete Summary**: `ADMIN_CRM_IMPLEMENTATION_COMPLETE.md`
- **API Docs**: http://localhost:8000/docs

## 🎯 Next Steps

1. ✅ Create your first super admin
2. ✅ Login to admin portal
3. ✅ Explore the dashboard
4. ✅ Create additional admins if needed
5. ✅ Start managing your platform!

---

Need help? Check the full documentation or contact support.

