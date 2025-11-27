# MTN Credentials Setup Checklist

Use this checklist to track your progress setting up MTN credentials.

---

## ☐ Phase 1: Register & Get Credentials (15-30 min)

### MTN Developer Account
- [ ] Register at https://developer.mtn.com/
- [ ] Verify email address
- [ ] Login to dashboard
- [ ] Complete profile information

### Create Application
- [ ] Create new app named "SusuSave"
- [ ] Subscribe to SMS API
- [ ] Subscribe to USSD/Mobile Messaging API
- [ ] Copy Consumer Key
- [ ] Copy Consumer Secret
- [ ] Note API Base URL for Ghana

### MTN Mobile Money Account
- [ ] Register at https://momodeveloper.mtn.com/
- [ ] Verify email address
- [ ] Login to MoMo dashboard
- [ ] Get Subscription Key
- [ ] Create API User (or run `python setup_mtn_momo.py`)
- [ ] Get API Key for user

---

## ☐ Phase 2: Configure Application (5 min)

### Update .env File
Location: `/Users/maham/susu/backend/.env`

- [ ] Update `MTN_CONSUMER_KEY` with your Consumer Key
- [ ] Update `MTN_CONSUMER_SECRET` with your Consumer Secret
- [ ] Update `MTN_BASE_URL` (check MTN docs for Ghana)
- [ ] Update `MTN_MOMO_SUBSCRIPTION_KEY`
- [ ] Update `MTN_MOMO_API_USER`
- [ ] Update `MTN_MOMO_API_KEY`
- [ ] Generate and set `SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Generate and set `ENCRYPTION_KEY` (use Python script)
- [ ] Set `USE_MTN_SERVICES=true`

---

## ☐ Phase 3: Set Up Public URL (5 min)

### Choose Your Option:

**Option A: ngrok (for testing)**
- [ ] Install ngrok: `brew install ngrok`
- [ ] Start ngrok: `ngrok http 8000`
- [ ] Copy the https URL (e.g., https://abc123.ngrok-free.app)
- [ ] Update `MTN_CALLBACK_URL` in .env with your ngrok URL + `/ussd/callback`

**Option B: Production Domain**
- [ ] Update `MTN_CALLBACK_URL` with your domain + `/ussd/callback`
- [ ] Ensure SSL certificate is valid
- [ ] Test URL is accessible from internet

### Register Callback
- [ ] Go to MTN Developer Portal
- [ ] Open SusuSave application settings
- [ ] Add callback URL to webhook/callback settings
- [ ] Save changes

---

## ☐ Phase 4: Test Integration (10 min)

### Restart Services
- [ ] Run: `docker-compose restart backend`
- [ ] Check logs: `docker logs sususave_backend --tail 50 --follow`
- [ ] Look for "Successfully obtained MTN access token"
- [ ] Verify no "418 I'm a teapot" errors

### Test Each Service

**Health Check:**
```bash
curl http://localhost:8000/ussd/health
```
- [ ] Status shows "healthy"
- [ ] Provider shows "MTN"

**USSD Test:**
```bash
cd /Users/maham/susu/backend
python test_africastalking_ussd.py test
```
- [ ] All 4 tests pass
- [ ] No authentication errors in logs

**SMS Test (optional, requires credits):**
```bash
# Test sending SMS to your phone
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+233XXXXXXXXX"}'
```
- [ ] SMS received on phone
- [ ] Check logs for confirmation

**Mobile Money Test:**
```bash
curl -X POST http://localhost:8000/payments/validate-account \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+233XXXXXXXXX"}'
```
- [ ] Account validation successful
- [ ] No MoMo errors in logs

---

## ☐ Phase 5: Production Preparation (Future)

### USSD Short Code
- [ ] Contact MTN Ghana for USSD code assignment
- [ ] Provide callback URL and app details
- [ ] Wait for approval (1-2 weeks)
- [ ] Update `MTN_USSD_SERVICE_CODE` in .env
- [ ] Test with real USSD code

### Move to Production
- [ ] Request production credentials from MTN
- [ ] Update .env with production keys
- [ ] Change `MTN_ENVIRONMENT=production`
- [ ] Change `MTN_MOMO_TARGET_ENVIRONMENT=production`
- [ ] Update `MTN_BASE_URL` to production endpoint
- [ ] Test thoroughly in production
- [ ] Monitor usage and costs

---

## 📋 Credentials Checklist

Keep track of what you have:

### MTN API (SMS & USSD)
```
[ ] Consumer Key: ____________________
[ ] Consumer Secret: _________________
[ ] Base URL: ________________________
[ ] Environment: sandbox / production
```

### MTN Mobile Money
```
[ ] Subscription Key: ________________
[ ] API User (UUID): _________________
[ ] API Key: _________________________
[ ] Environment: sandbox / production
```

### Application Security
```
[ ] SECRET_KEY: ______________________
[ ] ENCRYPTION_KEY: __________________
```

### Public URLs
```
[ ] Callback URL: ____________________
[ ] Registered with MTN: Yes / No
[ ] USSD Code: _______________________
[ ] Approved by MTN: Yes / No
```

---

## 🐛 Troubleshooting Checklist

If something doesn't work:

- [ ] Check .env file has no extra spaces
- [ ] Verify credentials copied correctly
- [ ] Ensure ngrok is running (if using)
- [ ] Check callback URL is accessible from internet
- [ ] Verify Docker container restarted
- [ ] Check logs for specific error messages
- [ ] Try credentials directly with curl
- [ ] Contact MTN support if credentials invalid

---

## 📞 Support Contacts

- **MTN API Support**: api.support@mtn.com
- **MTN Ghana**: api.support@mtn.com.gh
- **MTN Developer Portal**: https://developer.mtn.com/support
- **MoMo Support**: https://momodeveloper.mtn.com/support

---

## ✅ Success Indicators

You'll know everything is working when:

- ✅ Backend logs show "Successfully obtained MTN access token"
- ✅ No "418 I'm a teapot" errors
- ✅ Health check returns "healthy"
- ✅ All USSD tests pass
- ✅ SMS received on real phone (if testing)
- ✅ MoMo account validation works
- ✅ No authentication errors in logs

---

**Current Status**: ☐ Not Started / ☐ In Progress / ☐ Complete  
**Date Started**: ___________  
**Date Completed**: ___________

---

**Need Help?** See `MTN_CREDENTIALS_SETUP_GUIDE.md` for detailed instructions

