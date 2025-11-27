# AfricaTalking Integration Checklist

Use this checklist to set up and test your AfricaTalking USSD integration.

## Setup Checklist

### Phase 1: Account Setup
- [ ] Create AfricaTalking account at [account.africastalking.com](https://account.africastalking.com/)
- [ ] Verify email address
- [ ] Generate API key from Settings → API Key
- [ ] Note your sandbox USSD code (auto-assigned)

### Phase 2: Environment Configuration
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `env.example` to `.env`
- [ ] Add AfricaTalking credentials to `.env`:
  ```env
  AT_USERNAME=sandbox
  AT_API_KEY=atsk_xxxxxxxxxxxxx
  AT_ENVIRONMENT=sandbox
  AT_USSD_SERVICE_CODE=*384*12345#
  ```
- [ ] Set `ENABLE_REAL_SMS=True` if you want real SMS (optional)

### Phase 3: Local Development Setup
- [ ] Start backend server: `python -m uvicorn app.main:app --reload --port 8000`
- [ ] Install ngrok: `brew install ngrok` (or download)
- [ ] Start ngrok: `ngrok http 8000`
- [ ] Copy ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
- [ ] Update AfricaTalking callback URL to: `https://abc123.ngrok.io/ussd/callback`

### Phase 4: Testing
- [ ] Test health endpoint: `curl http://localhost:8000/ussd/health`
- [ ] Run test script: `python test_africastalking_ussd.py test`
- [ ] Test in AfricaTalking web simulator
- [ ] Download AfricaTalking Sandbox app (optional)
- [ ] Test all menu options:
  - [ ] 1. Join Group
  - [ ] 2. Pay Contribution
  - [ ] 3. Check Balance/Status
  - [ ] 4. My Payout Date

### Phase 5: Create Test Data
- [ ] Register test user via API
- [ ] Create test group via API
- [ ] Note group code
- [ ] Test joining group via USSD
- [ ] Verify SMS notifications (if enabled)

### Phase 6: Production Preparation
- [ ] Apply for production USSD code (takes 2-5 business days)
- [ ] Add funds to AfricaTalking account
- [ ] Deploy backend to production server
- [ ] Set up SSL certificate
- [ ] Update production `.env`:
  ```env
  AT_USERNAME=your_live_username
  AT_API_KEY=atsk_production_key
  AT_ENVIRONMENT=production
  AT_USSD_SERVICE_CODE=*920*55#
  ```
- [ ] Update callback URL in AfricaTalking dashboard
- [ ] Test in production environment
- [ ] Monitor logs for errors

## Testing Scenarios

### Scenario 1: New User Joins Group
1. [ ] Dial USSD code
2. [ ] Select "1" (Join Group)
3. [ ] Enter valid group code
4. [ ] Verify success message
5. [ ] Check SMS received (if enabled)
6. [ ] Verify user created in database
7. [ ] Verify membership created

### Scenario 2: User Makes Payment
1. [ ] Dial USSD code
2. [ ] Select "2" (Pay Contribution)
3. [ ] Select group from list
4. [ ] Verify payment confirmation
5. [ ] Check SMS received (if enabled)
6. [ ] Verify payment in database

### Scenario 3: User Checks Status
1. [ ] Dial USSD code
2. [ ] Select "3" (Check Balance/Status)
3. [ ] Verify correct status displayed
4. [ ] Test with no groups
5. [ ] Test with multiple groups

### Scenario 4: User Checks Payout Date
1. [ ] Dial USSD code
2. [ ] Select "4" (My Payout Date)
3. [ ] Verify payout information
4. [ ] Test "next to receive" scenario
5. [ ] Test "already received" scenario
6. [ ] Test "future rounds" scenario

### Scenario 5: Error Handling
1. [ ] Test invalid group code
2. [ ] Test invalid menu option
3. [ ] Test timeout (wait 30+ seconds)
4. [ ] Test session interruption
5. [ ] Test database errors (stop DB)
6. [ ] Test network errors (stop ngrok)

## Common Issues & Solutions

### Issue: Callback not reached
- [ ] Verify ngrok is running
- [ ] Check ngrok URL is HTTPS
- [ ] Verify backend is running
- [ ] Check firewall settings
- [ ] Test manually with curl

### Issue: USSD shows blank/error
- [ ] Check response format (starts with CON/END)
- [ ] Verify response is plain text
- [ ] Check for exceptions in logs
- [ ] Ensure response time < 8 seconds
- [ ] Check message length < 160 chars

### Issue: Session lost/timeout
- [ ] Verify session storage working
- [ ] Check response time
- [ ] Look for exceptions clearing session
- [ ] Consider using Redis for persistence

### Issue: SMS not sending
- [ ] Verify `ENABLE_REAL_SMS=True`
- [ ] Check AfricaTalking credentials
- [ ] Verify phone number format (+256...)
- [ ] Check account balance (production)
- [ ] Review SMS logs in dashboard

## Performance Checklist

- [ ] Response time < 3 seconds (target)
- [ ] Response time < 8 seconds (maximum)
- [ ] Database queries optimized
- [ ] Session storage efficient
- [ ] Error logging enabled
- [ ] Monitoring set up

## Security Checklist

- [ ] HTTPS only (production)
- [ ] API keys in environment variables
- [ ] No sensitive data in logs
- [ ] Phone numbers encrypted in database
- [ ] Input validation on all fields
- [ ] Rate limiting enabled
- [ ] Session timeout configured

## Documentation

- [ ] Read [USSD_QUICKSTART.md](docs/USSD_QUICKSTART.md)
- [ ] Read [AFRICASTALKING_SETUP.md](docs/AFRICASTALKING_SETUP.md)
- [ ] Review [AfricaTalking Docs](https://developers.africastalking.com/docs/ussd/overview)
- [ ] Review [Best Practices](https://developers.africastalking.com/docs/ussd/best_practices)

## Support Resources

- [ ] Bookmark AfricaTalking dashboard
- [ ] Join AfricaTalking community forum
- [ ] Save support email: support@africastalking.com
- [ ] Document your USSD flow
- [ ] Set up monitoring/alerts

---

## Quick Commands Reference

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start ngrok
ngrok http 8000

# Run tests
python test_africastalking_ussd.py test

# Check health
curl http://localhost:8000/ussd/health

# Simulate USSD request
curl -X POST http://localhost:8000/ussd/callback \
  -d "sessionId=test123" \
  -d "serviceCode=*384*12345#" \
  -d "phoneNumber=+254700000001" \
  -d "text="

# View SMS logs
tail -f sms_logs.txt

# Check database
psql -U sususer -d sususave
```

---

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Completed

Update this checklist as you progress through your integration!

