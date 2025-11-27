# PWA Login Fix ✅

## Issue Found
The PWA login was failing because the frontend was sending data in the wrong format to the backend.

### The Problem:
- **Backend Expected:** JSON format with fields `phone_number` and `password`
- **Frontend Was Sending:** Form-urlencoded data with fields `username` and `password`

### What Was Fixed:

**File:** `/Users/maham/susu/web/app/src/api/authService.ts`

**Before:**
```typescript
async login(data: LoginRequest): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', data.phone_number);  // ❌ Wrong field name
  formData.append('password', data.password);

  const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',  // ❌ Wrong format
    },
  });
  return response.data;
}
```

**After:**
```typescript
async login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', {
    phone_number: data.phone_number,  // ✅ Correct field name
    password: data.password,
  });
  return response.data;
}
```

## Backend Endpoint

The backend `/auth/login` endpoint expects:
```python
class UserLogin(BaseModel):
    phone_number: str
    password: str
```

And returns:
```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

## Testing the Fix

### 1. Start the Backend
```bash
cd /Users/maham/susu/backend
python -m app.main
```

### 2. Start the PWA
```bash
cd /Users/maham/susu/web/app
npm run dev
```

### 3. Test Login

You can test with existing users or create a new one:

#### Create a Test User (via API):
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "name": "Test User",
    "password": "password123",
    "user_type": "app"
  }'
```

#### Login via PWA:
1. Open the PWA at `http://localhost:5173/app/login`
2. Enter phone number: `+233244123456`
3. Enter password: `password123`
4. Click "Login"

#### Login via API (to verify):
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+233244123456",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## Alternative: OTP Login

The PWA also supports OTP-based login (no password required):

1. Enter phone number
2. Click "Login with OTP"
3. Enter the OTP code sent to your phone
4. Access granted

## Status
✅ Login format fixed
✅ Field names corrected
✅ Backend server started
✅ PWA dev server started
✅ Ready for testing

## Next Steps
1. Test login with an existing user
2. If no users exist, create one using the registration endpoint
3. Verify token is stored and dashboard loads correctly

