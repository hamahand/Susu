# USSD Testing Guide

**Status**: ✅ USSD Service Fully Functional  
**Date**: October 23, 2025

## Quick Test Commands

### Test USSD Endpoint Directly

```bash
# Test main menu (initial request)
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=test123&serviceCode=*920*55%23&phoneNumber=%2B233244555555&text="

# Expected Response:
# CON Welcome to SusuSave
# 1. Join Group
# 2. Pay Contribution
# 3. Check Balance/Status
# 4. My Payout Date
```

### Test USSD with User Input

```bash
# Select option 1 (Join Group)
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=test123&serviceCode=*920*55%23&phoneNumber=%2B233244555555&text=1"

# Expected Response:
# CON Enter Group Code (e.g., SUSU1234):
```

```bash
# Enter a group code
curl -X POST http://localhost:8000/ussd/callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=test123&serviceCode=*920*55%23&phoneNumber=%2B233244555555&text=1*SUSU1234"
```

### Check USSD Health

```bash
curl http://localhost:8000/ussd/health
```

## Automated Testing

### Run All USSD Tests

```bash
cd /Users/maham/susu/backend
python test_africastalking_ussd.py test
```

**Expected Output:**
```
============================================================
Running Automated USSD Tests
============================================================

Test 1: Display Main Menu
✓ Main menu displayed correctly

Test 2: Check Status (Empty Groups)
✓ Status check works

Test 3: Invalid Menu Option
✓ Invalid option handled correctly

Test 4: Join Group (Enter Code)
✓ Join group flow initiated

============================================================
All automated tests passed!
============================================================
```

### Interactive USSD Session

```bash
cd /Users/maham/susu/backend
python test_africastalking_ussd.py
```

This starts an interactive USSD simulator where you can:
- See the full USSD menu
- Enter options interactively
- Test the complete user flow

## USSD Menu Options

### Option 1: Join Group
- Enter a group code (e.g., SUSU1234)
- System creates USSD user if not exists
- Adds user to the group
- Returns success message with group details

### Option 2: Pay Contribution
- Shows list of groups user has joined
- Select group number to pay
- Processes payment
- Sends SMS confirmation (mock in dev)

### Option 3: Check Balance/Status
- Shows all groups user is in
- Displays position, round, contribution amount
- No input required

### Option 4: My Payout Date
- Shows when user will receive payout
- Displays expected amount
- Shows position in rotation

## Monitoring

### Watch Backend Logs

```bash
# Follow logs in real-time
docker logs sususave_backend --tail 50 --follow

# Check for USSD-specific logs
docker logs sususave_backend 2>&1 | grep -i "ussd"

# Check for errors
docker logs sususave_backend 2>&1 | grep -i "error"
```

### Check SMS Logs

```bash
# View sent SMS (mock logs)
tail -f /Users/maham/susu/backend/sms_logs.txt
```

## Testing with Real Phone Numbers

### Using AfricasTalking (If Configured)

1. Set up ngrok for public URL:
   ```bash
   ngrok http 8000
   ```

2. Update callback URL in `.env`:
   ```env
   MTN_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/ussd/callback
   ```

3. Register USSD code with AfricasTalking:
   - Login to [AfricasTalking Dashboard](https://account.africastalking.com/)
   - Go to USSD section
   - Register your callback URL
   - Get assigned USSD code (e.g., *384*12345#)

4. Test by dialing from a real phone:
   ```
   *384*12345#
   ```

### Using MTN (When Configured)

1. Get valid MTN credentials from [MTN Developer Portal](https://developer.mtn.com/)

2. Update `.env`:
   ```env
   MTN_CONSUMER_KEY=your_key
   MTN_CONSUMER_SECRET=your_secret
   USE_MTN_SERVICES=true
   MTN_USSD_SERVICE_CODE=*920*55#
   ```

3. Register callback URL with MTN

4. Test by dialing:
   ```
   *920*55#
   ```

## Troubleshooting

### USSD Returns Error

```bash
# Check if backend is running
docker ps | grep backend

# Check backend logs
docker logs sususave_backend --tail 100

# Restart backend
docker-compose restart backend
```

### MTN Authentication Fails

**This is expected in development!** The system falls back to mock services.

To check status:
```bash
curl http://localhost:8000/ussd/health
```

See `MTN_USSD_ERROR_DIAGNOSIS.md` for full details.

### Database Connection Issues

```bash
# Check if database is running
docker ps | grep postgres

# Check database health
docker exec sususave_db pg_isready -U sususer

# Restart database
docker-compose restart db
```

## Test Scenarios

### Scenario 1: New User Joins Group via USSD

1. Start USSD session (dial code or use curl)
2. Select option 1 (Join Group)
3. Enter valid group code
4. User is created automatically
5. User joins group
6. Receives SMS with group details

### Scenario 2: Existing User Makes Payment

1. Start USSD session
2. Select option 2 (Pay Contribution)
3. View list of joined groups
4. Select group number
5. Payment processed
6. Receives SMS confirmation

### Scenario 3: Check Status

1. Start USSD session
2. Select option 3 (Check Balance/Status)
3. View all groups and positions
4. Session ends

### Scenario 4: Check Payout Date

1. Start USSD session
2. Select option 4 (My Payout Date)
3. View payout schedule for all groups
4. Session ends

## Files Reference

- **USSD Router**: `backend/app/routers/ussd.py`
- **USSD Service**: `backend/app/services/ussd_service.py`
- **MTN Integration**: `backend/app/integrations/mtn_ussd_integration.py`
- **SMS Sender**: `backend/app/integrations/sms_sender.py`
- **Config**: `backend/app/config.py`
- **Tests**: `backend/test_africastalking_ussd.py`

## API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Look for the **USSD** section for endpoint details.

## Support

For issues or questions:
1. Check `MTN_USSD_ERROR_DIAGNOSIS.md`
2. Review backend logs
3. Run automated tests
4. Check this guide for common scenarios

---

**Last Updated**: October 23, 2025  
**Status**: All USSD Tests Passing ✅

