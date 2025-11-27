# Admin System Setup Guide

## Overview

This guide will help you set up the SusuSave Admin CRM system, including database migrations, creating the first super admin, and accessing the admin portal.

## Prerequisites

- Backend server running (FastAPI)
- PostgreSQL database configured
- Python environment with all dependencies installed

## Step 1: Run Database Migration

The admin system requires new database tables and fields. Run the Alembic migration:

```bash
cd backend
alembic upgrade head
```

This will:
- Add `is_system_admin`, `admin_role`, and `last_login` fields to the `users` table
- Create the `system_settings` table
- Create the `adminrole` enum type

## Step 2: Create First Super Admin

Run the super admin creation script:

```bash
cd backend
python create_super_admin.py
```

Follow the prompts to enter:
- Admin Name
- Phone Number (with country code, e.g., +233201234567)
- Password (minimum 6 characters)
- Confirm Password

Example:
```
🔐 Create Super Admin Account
==================================================
Admin Name: John Doe
Phone Number (with country code, e.g., +233201234567): +233201234567
Password (min 6 characters): ******
Confirm Password: ******

==================================================
✅ Super Admin Created Successfully!
==================================================
   ID: 1
   Name: John Doe
   Phone: +233201234567
   Role: super_admin

🔑 You can now log in to the admin portal with these credentials.
   Admin API: http://localhost:8000/admin/
   API Docs: http://localhost:8000/docs#/Admin
```

## Step 3: Set Up Admin Frontend

Install dependencies and start the admin portal:

```bash
cd web/admin
npm install
npm run dev
```

The admin portal will be available at: **http://localhost:3001**

## Step 4: Login to Admin Portal

1. Open http://localhost:3001 in your browser
2. Enter the phone number and password you created
3. Click "Login"

You should now have access to the full admin portal!

## Admin Roles

There are three admin role levels:

1. **SUPER_ADMIN**: Full access to all features, including:
   - Create/manage other admins
   - Delete groups
   - Update system settings
   - All other admin functions

2. **FINANCE_ADMIN**: Financial management focus:
   - Approve/reject payouts
   - Manage payments
   - View financial reports
   - Cannot manage admins or system settings

3. **SUPPORT_ADMIN**: User support focus:
   - Manage users
   - Verify KYC
   - Manage groups
   - Cannot manage finances or system settings

## Creating Additional Admins

Only super admins can create additional admin users.

### Via Admin Portal:
1. Login as super admin
2. Go to Settings → Admin Management
3. Click "Create Admin"
4. Fill in details and select role
5. Submit

### Via API:
```bash
curl -X POST http://localhost:8000/admin/admins \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233201234568",
    "name": "Jane Smith",
    "password": "securepass123",
    "admin_role": "finance_admin"
  }'
```

## Environment Configuration

Add admin-related settings to your `.env` file if needed:

```env
# Admin settings (optional)
ADMIN_SESSION_TIMEOUT=3600  # 1 hour
ADMIN_MAX_LOGIN_ATTEMPTS=5
```

## Security Best Practices

1. **Strong Passwords**: Enforce minimum password requirements
2. **Regular Audits**: Review audit logs regularly
3. **Limit Super Admins**: Only create super admin accounts when necessary
4. **Monitor Activity**: Check the dashboard for suspicious activity
5. **Secure Deployment**: Use HTTPS in production
6. **Rotate Credentials**: Change admin passwords periodically

## Troubleshooting

### Migration Fails
```bash
# Check current migration
alembic current

# If needed, stamp to specific version
alembic stamp head

# Try upgrade again
alembic upgrade head
```

### Can't Create Admin - User Exists
If a regular user exists with the same phone number, you can promote them:
1. Run `create_super_admin.py`
2. Enter the existing phone number
3. Choose 'y' when prompted to promote

### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd web/admin
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues
Check that:
1. Backend is running on port 8000
2. CORS is configured correctly in `backend/app/config.py`
3. Vite proxy is configured in `web/admin/vite.config.ts`

## Production Deployment

### Backend
1. Set secure `SECRET_KEY` in production
2. Use production database
3. Enable HTTPS
4. Set appropriate CORS origins
5. Configure rate limiting

### Frontend
```bash
cd web/admin
npm run build
```

Serve the `dist/` folder with your web server (Nginx, Apache, etc.)

Example Nginx config:
```nginx
server {
    listen 443 ssl;
    server_name admin.sususave.com;

    root /var/www/admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /admin {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Navigate to the "Admin" tag to see all admin endpoints.

## Support

For issues or questions:
1. Check audit logs for error details
2. Review backend logs
3. Consult the API documentation
4. Contact system administrator

