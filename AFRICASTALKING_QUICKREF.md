# AfricaTalking USSD - Quick Reference

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Get credentials from https://account.africastalking.com
# 2. Configure
cd backend
cp env.example .env
# Add: AT_USERNAME=sandbox, AT_API_KEY=your_key

# 3. Start
python -m uvicorn app.main:app --reload --port 8000

# 4. Expose (new terminal)
ngrok http 8000

# 5. Set callback in AT dashboard
# https://your-ngrok-url.ngrok.io/ussd/callback

# 6. Test
python test_africastalking_ussd.py
```

## 📋 USSD Menu

```
*384*12345#
├─ 1. Join Group      → Enter code → Success/Error
├─ 2. Pay             → Select group → Confirm
├─ 3. Status          → Show all groups
└─ 4. Payout Date     → Show schedule
```

## 🔧 Configuration

**`.env` file:**
```env
AT_USERNAME=sandbox
AT_API_KEY=atsk_xxxxx
AT_ENVIRONMENT=sandbox
AT_USSD_SERVICE_CODE=*384*12345#
ENABLE_REAL_SMS=False
```

## 🧪 Testing

```bash
# Automated tests
python test_africastalking_ussd.py test

# Interactive
python test_africastalking_ussd.py

# curl test
./test_ussd_curl.sh

# Manual
curl -X POST http://localhost:8000/ussd/callback \
  -d "sessionId=test" \
  -d "serviceCode=*384*12345#" \
  -d "phoneNumber=+256700000001" \
  -d "text="
```

## 📡 Response Format

**Continue:**
```
CON Welcome to SusuSave
1. Join Group
2. Pay Contribution
```

**End:**
```
END Success! Payment confirmed.
```

## 🌐 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ussd/callback` | POST | USSD callback (AT) |
| `/ussd/health` | GET | Health check |

## 🔐 Request Parameters (from AfricaTalking)

```
sessionId    : string  (unique session ID)
serviceCode  : string  (*384*12345#)
phoneNumber  : string  (+256700000001)
text         : string  (user input, * separated)
```

## 📱 Phone Number Format

- **Required:** Include country code
- **Example:** `+256700000001` (Uganda)
- **Example:** `+233244123456` (Ghana)
- **Example:** `+254712345678` (Kenya)

## ⏱️ Timing

- **Response time:** < 8 seconds (hard limit)
- **Target:** < 3 seconds
- **Session timeout:** ~30 seconds idle

## 🐛 Debug

```bash
# Check health
curl http://localhost:8000/ussd/health

# View logs
tail -f sms_logs.txt

# Check ngrok requests
open http://localhost:4040

# AfricaTalking logs
# Dashboard → USSD → Logs
```

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| Callback not reached | Check ngrok running, use HTTPS |
| Blank screen | Verify response starts with CON/END |
| Session lost | Check response time < 8s |
| Invalid input | Validate and sanitize all inputs |

## 📚 File Locations

```
backend/
├── app/routers/ussd.py                  # Endpoint
├── app/services/ussd_service.py         # Logic
├── app/integrations/
│   ├── africastalking_integration.py    # AT SDK
│   └── sms_sender.py                    # SMS helper
├── test_africastalking_ussd.py          # Tests
├── test_ussd_curl.sh                    # Curl tests
└── docs/
    ├── AFRICASTALKING_SETUP.md          # Full guide
    └── USSD_QUICKSTART.md               # Quick start
```

## 🎯 Production Checklist

- [ ] Apply for USSD code (2-5 days)
- [ ] Switch to live credentials
- [ ] Deploy with HTTPS
- [ ] Update callback URL
- [ ] Enable SMS (`ENABLE_REAL_SMS=True`)
- [ ] Add monitoring
- [ ] Test all flows

## 🔗 Resources

- **Setup Guide:** `backend/docs/AFRICASTALKING_SETUP.md`
- **Checklist:** `backend/AFRICASTALKING_CHECKLIST.md`
- **AT Docs:** https://developers.africastalking.com/docs/ussd
- **Dashboard:** https://account.africastalking.com/

## 💡 Tips

1. **ngrok restarts?** Update callback URL each time
2. **Testing?** Use AfricaTalking web simulator
3. **Messages?** Keep under 160 chars
4. **Errors?** Always return valid CON/END response
5. **Production?** Use Redis for sessions

## 🆘 Support

- **AT Support:** support@africastalking.com
- **Forum:** community.africastalking.com
- **Docs:** Full guides in `/backend/docs/`

---

**Quick test:** `python test_africastalking_ussd.py test`

