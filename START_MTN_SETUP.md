# 🚀 Start MTN Setup - Quick Reference

**Choose your path:**

---

## Path 1: Interactive Setup (Easiest) ⚡

If you already have MTN credentials:

```bash
cd /Users/maham/susu/backend
python3 setup_mtn_credentials.py
```

This script will:
- ✅ Ask for your credentials interactively
- ✅ Update your .env file automatically
- ✅ Generate security keys
- ✅ Show you next steps

**Time: 5 minutes**

---

## Path 2: Manual Setup (More Control) 🔧

### Step 1: Get Credentials

Visit these sites and register:
1. **MTN API**: https://developer.mtn.com/
2. **MTN MoMo**: https://momodeveloper.mtn.com/

### Step 2: Edit .env

```bash
cd /Users/maham/susu/backend
nano .env  # or use your preferred editor
```

Update these lines:

```env
# MTN API
MTN_CONSUMER_KEY=your_consumer_key_here
MTN_CONSUMER_SECRET=your_consumer_secret_here
MTN_BASE_URL=https://sandbox.api.mtn.com/v1
MTN_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/ussd/callback

# MTN MoMo
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key
MTN_MOMO_API_USER=your_api_user_uuid
MTN_MOMO_API_KEY=your_api_key

# Enable
USE_MTN_SERVICES=true
ENABLE_MTN_USSD=true
ENABLE_MTN_SMS=true
```

### Step 3: Set Up ngrok

```bash
# Install
brew install ngrok

# Run
ngrok http 8000

# Copy the https URL and update MTN_CALLBACK_URL in .env
```

### Step 4: Restart & Test

```bash
cd /Users/maham/susu
docker-compose restart backend
docker logs sususave_backend --tail 50 --follow

# Look for: "Successfully obtained MTN access token"
```

**Time: 15 minutes**

---

## Path 3: I Don't Have Credentials Yet 📋

Follow the complete guide:

```bash
# Read this first
cat /Users/maham/susu/MTN_CREDENTIALS_SETUP_GUIDE.md

# Or open in browser
open /Users/maham/susu/MTN_CREDENTIALS_SETUP_GUIDE.md

# Track your progress
open /Users/maham/susu/MTN_SETUP_CHECKLIST.md
```

**Time: 30 minutes + MTN approval time**

---

## Quick Test Commands

After setup:

```bash
# 1. Health check
curl http://localhost:8000/ussd/health

# 2. Run tests
cd /Users/maham/susu/backend
python test_africastalking_ussd.py test

# 3. Check for errors
docker logs sususave_backend 2>&1 | grep -i "error\|token"
```

**Success = No "418 I'm a teapot" errors! ✅**

---

## 🆘 Need Help?

| Issue | Solution |
|-------|----------|
| Don't have credentials | See `MTN_CREDENTIALS_SETUP_GUIDE.md` |
| Setup script errors | Check Python 3 installed: `python3 --version` |
| 418 errors still | Credentials invalid - check MTN portal |
| Can't edit .env | Use: `open -a TextEdit .env` |
| Forgot what to do | Check `MTN_SETUP_CHECKLIST.md` |

---

## 📚 All Documentation

- **START_MTN_SETUP.md** ← You are here (quick start)
- **MTN_CREDENTIALS_SETUP_GUIDE.md** (detailed guide, 200+ lines)
- **MTN_SETUP_CHECKLIST.md** (track progress)
- **USSD_TESTING_GUIDE.md** (test after setup)
- **MTN_USSD_ERROR_DIAGNOSIS.md** (troubleshooting)

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Register at MTN portals | 10 min |
| Get API credentials | 5 min |
| Configure .env file | 5 min |
| Set up ngrok | 2 min |
| Test integration | 3 min |
| **Total** | **25 min** |

*(Plus waiting time for MTN approvals)*

---

## 💡 Pro Tips

1. **Use Sandbox First**: Always test with sandbox before production
2. **Keep Credentials Safe**: Never commit .env to git
3. **Use ngrok for Testing**: Easier than setting up production domain
4. **Check Logs Often**: They tell you exactly what's wrong
5. **Test Each Step**: Don't skip the health checks

---

## ✅ Success Checklist

You'll know it worked when:

- [ ] No "418 I'm a teapot" in logs
- [ ] Health check shows "healthy"
- [ ] Logs show "Successfully obtained MTN access token"
- [ ] USSD tests all pass
- [ ] Can send SMS to real phone (optional)

---

**Ready? Pick a path above and let's go! 🚀**

