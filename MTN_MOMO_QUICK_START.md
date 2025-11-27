# 🚀 MTN MoMo Payment Flow - Quick Start

**Get payments working in 10 minutes!**

---

## ⚡ Super Quick Setup

```bash
# 1. Run setup script
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py

# 2. Start ngrok
ngrok http 8000

# 3. Restart backend
cd /Users/maham/susu
docker-compose restart backend

# 4. Test it!
cd backend
python3 test_mtn_momo_payment.py
```

**Done!** 🎉

---

##  What's Available Now

### ✅ User Features
- Click "Pay Now" on unpaid contributions
- Receive MoMo prompt on phone
- Auto-updates when paid

### ✅ Admin Features
- Click "Request Payment" on any unpaid member
- Member receives MoMo prompt
- Track payment status in real-time

---

## 📱 How It Works

### User Pays:
1. User sees unpaid status in dashboard
2. Clicks "💳 Pay Now"
3. Gets MoMo prompt on phone: "Pay GHS XX.XX to SusuSave"
4. Approves payment
5. Status updates to "Paid" ✅

### Admin Requests Payment:
1. Admin sees member with unpaid status
2. Clicks "📱 Request Payment"
3. Member gets MoMo prompt on their phone
4. Member approves
5. Admin sees status update ✅

---

## 🧪 Test Numbers (Sandbox)

**Auto-Approve:**
```
+233240000001
+233240000002
+233240000003
```

**Auto-Reject:**
```
+233240000100
+233240000101
```

Use these for testing without a real phone!

---

## 🎯 Quick Test

### Test 1: Pay Your Own Contribution

1. Login to web app: http://localhost:5173
2. Go to your group dashboard
3. Look for your name with "Unpaid" badge
4. Click "💳 Pay Now"
5. Check phone for MoMo prompt (or check logs if using test number)

### Test 2: Admin Requests Payment

1. Login as admin
2. Go to group dashboard
3. Find member with "Unpaid" badge
4. Click "📱 Request Payment" next to their name
5. Member receives prompt

### Test 3: Check Payment Status

```bash
# Watch backend logs
docker logs sususave_backend --tail 50 --follow

# Look for:
# ✅ "Payment request sent: {reference_id}"
# ✅ "Successfully obtained MTN MoMo access token"
```

---

## 📋 What You Need

Before setup:
- [ ] MTN MoMo Developer account
- [ ] Collections Subscription Key
- [ ] ngrok installed

---

## 🔧 Setup Details

### 1. Get Subscription Key

```
1. Go to: https://momodeveloper.mtn.com/
2. Sign up / Login
3. Subscribe to "Collections" product
4. Copy your Primary Key
```

### 2. Run Setup Script

```bash
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py

# Enter when prompted:
# - Subscription Key: your_key_here
# - Callback Host: your-ngrok-url.ngrok-free.app
```

The script will:
- ✅ Create API User
- ✅ Generate API Key
- ✅ Test authentication
- ✅ Update .env file

### 3. Start ngrok

```bash
ngrok http 8000

# Copy the https URL
# Example: https://abc123.ngrok-free.app
```

### 4. Update Callback URL

The setup script asks for this, but if you need to change it:

```env
# In backend/.env
MTN_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/ussd/callback
```

### 5. Restart Backend

```bash
cd /Users/maham/susu
docker-compose restart backend

# Check logs
docker logs sususave_backend --tail 50 --follow
```

Look for:
```
✅ MTN MoMo Integration initialized - Environment: sandbox
✅ Successfully obtained MTN MoMo access token
```

---

## 🎮 Using the Features

### In Web App (Frontend)

#### For Users:
1. Navigate to group dashboard
2. Find your contribution status
3. If "Unpaid", click "💳 Pay Now"
4. Confirm in popup
5. Check phone for MoMo prompt

#### For Admins:
1. Navigate to group dashboard
2. See all members and their payment status
3. For unpaid members, click "📱 Request Payment"
4. Confirm who you're requesting from
5. Member receives prompt

### Via API (Backend)

#### User Pays Own Payment:
```bash
curl -X POST http://localhost:8000/payments/{payment_id}/pay-now \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Admin Requests Payment:
```bash
curl -X POST http://localhost:8000/payments/admin/request-payment \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "user_id": 2,
    "round_number": 1
  }'
```

#### Check Payment Status:
```bash
curl http://localhost:8000/payments/{payment_id}/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Troubleshooting

### "Failed to obtain MTN MoMo token"

**Solution:**
```bash
# Re-run setup
python3 setup_mtn_momo.py

# Check credentials
cat backend/.env | grep MTN_MOMO
```

### "Payment request failed"

**Check:**
1. Is backend running? `docker ps`
2. Is ngrok running? `curl https://your-ngrok-url.ngrok-free.app/`
3. Are credentials valid? Check logs

**Fix:**
```bash
# View detailed logs
docker logs sususave_backend | grep -i "momo\|payment"
```

### Phone number format errors

MTN expects: `233XXXXXXXXX` (no +, no spaces)

**Fix:** The system handles this automatically, but if you see errors:
- Good: `233244123456`
- Bad: `+233244123456` or `0244123456`

---

## 📚 Full Documentation

- **Complete Guide**: `MTN_MOMO_SANDBOX_SETUP.md`
- **Setup Script**: `backend/setup_mtn_momo.py`
- **Test Script**: `backend/test_mtn_momo_payment.py`
- **Integration Code**: `backend/app/integrations/mtn_momo_integration.py`

---

## ✅ Success Checklist

- [ ] Subscription key obtained
- [ ] Setup script completed
- [ ] ngrok running
- [ ] Backend restarted
- [ ] Logs show "Successfully obtained MTN MoMo access token"
- [ ] Can see payment buttons in web app
- [ ] Test payment works

---

## 🎯 Next Steps

1. **Test in Sandbox**
   - Use test phone numbers
   - Try both user and admin flows
   - Verify status updates

2. **Go to Production**
   - Get production subscription key
   - Update credentials
   - Test with small amounts first

3. **Monitor**
   - Watch logs for errors
   - Check payment success rates
   - Monitor MTN API usage

---

**Time to Setup**: 10 minutes  
**Difficulty**: Easy  
**Status**: Ready to Use

---

**Need Help?** See `MTN_MOMO_SANDBOX_SETUP.md` for detailed guide.

