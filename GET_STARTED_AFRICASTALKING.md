# 🚀 Get Started with AfricaTalking USSD

**Your complete guide to getting USSD up and running in 10 minutes!**

---

## ⚡ Super Quick Start (5 commands)

```bash
# 1. Setup
cd backend
./setup_africastalking.sh

# 2. Start backend
python -m uvicorn app.main:app --reload --port 8000

# 3. Start ngrok (new terminal)
ngrok http 8000

# 4. Configure AfricaTalking
# Copy ngrok URL → AT Dashboard → USSD → Callback URL

# 5. Test
python test_africastalking_ussd.py
```

**That's it!** 🎉

---

## 📋 Step-by-Step Guide

### Step 1: Get AfricaTalking Account (2 minutes)

1. Go to https://account.africastalking.com/auth/register
2. Sign up (completely free)
3. Click on **Settings** → **API Key**
4. Click **Generate** and copy your API key
5. Note: You're automatically in "sandbox" environment

### Step 2: Configure Your Project (2 minutes)

**Option A: Automatic Setup (Recommended)**
```bash
cd backend
./setup_africastalking.sh
```
Follow the prompts to enter your credentials.

**Option B: Manual Setup**
```bash
cd backend
cp env.example .env
nano .env  # or use your favorite editor
```

Add these lines:
```env
AT_USERNAME=sandbox
AT_API_KEY=your_api_key_from_step_1
AT_ENVIRONMENT=sandbox
AT_USSD_SERVICE_CODE=*384*12345#
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This installs the AfricaTalking Python SDK and all other dependencies.

### Step 4: Start Your Backend (1 minute)

```bash
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 5: Expose with ngrok (2 minutes)

**Open a NEW terminal window:**

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123def456.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123def456.ngrok.io`)

⚠️ **Important:** 
- Use the HTTPS URL (not HTTP)
- Each time you restart ngrok, you get a new URL
- You'll need to update AfricaTalking when the URL changes

### Step 6: Configure AfricaTalking (2 minutes)

1. Go to https://account.africastalking.com/
2. Click **USSD** in the left menu
3. Click **Create Channel**
4. Fill in:
   - **Name:** SusuSave USSD
   - **Callback URL:** `https://your-ngrok-url.ngrok.io/ussd/callback`
     (Replace with your actual ngrok URL from Step 5)
5. Click **Create**
6. **Note your USSD code** (e.g., `*384*12345#`)

### Step 7: Test! (1 minute)

**Option A: Test Script (Recommended for first test)**
```bash
cd backend
python test_africastalking_ussd.py
```

**Option B: AfricaTalking Web Simulator**
1. In AT dashboard, click **USSD** → **Simulator**
2. Enter test phone: `+254700000001`
3. Enter your USSD code: `*384*12345#`
4. Click **Dial**
5. Interact with your menu!

**Option C: Mobile App**
1. Download "AfricaTalking Sandbox" app (iOS/Android)
2. Log in with your AT credentials
3. Dial your USSD code
4. Test on actual phone!

---

## 🎯 What You Should See

### Initial Screen
```
CON Welcome to SusuSave
1. Join Group
2. Pay Contribution
3. Check Balance/Status
4. My Payout Date
```

### After Selecting Option 1 (Join Group)
```
CON Enter Group Code (e.g., SUSU1234):
```

### After Entering a Group Code
```
END Success! You joined [Group Name].
Position: [X]
Contribution: GHS [amount]
You will receive an SMS with details.
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend running on port 8000
- [ ] ngrok running and showing HTTPS URL
- [ ] Can access `http://localhost:8000/docs` (Swagger UI)
- [ ] Can access `http://localhost:8000/ussd/health` (returns JSON)
- [ ] AfricaTalking callback URL configured
- [ ] Test script runs without errors
- [ ] Can see main menu in AT simulator
- [ ] Can navigate through USSD menu

---

## 🐛 Troubleshooting

### "Connection refused" when starting backend
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 [PID]

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### "ngrok not found"
```bash
# macOS
brew install ngrok

# Or download from
# https://ngrok.com/download
```

### "Callback URL not reachable" in AfricaTalking
```bash
# 1. Make sure ngrok is running
ps aux | grep ngrok

# 2. Test your endpoint manually
curl https://your-ngrok-url.ngrok.io/ussd/health

# 3. Check you're using HTTPS (not HTTP)

# 4. Verify no firewall blocking
```

### USSD shows blank screen
```bash
# 1. Check backend logs for errors
# Look at the terminal where uvicorn is running

# 2. Test endpoint manually
curl -X POST http://localhost:8000/ussd/callback \
  -d "sessionId=test" \
  -d "serviceCode=*384*12345#" \
  -d "phoneNumber=+254700000001" \
  -d "text="

# Should return: "CON Welcome to SusuSave..."
```

### Python dependencies installation fails
```bash
# Create a virtual environment first
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Then install
pip install -r requirements.txt
```

---

## 📱 Testing Different Flows

### Test 1: Check Status (No Groups)
1. Dial USSD code
2. Enter `3`
3. Should see: "You are not a member of any group"

### Test 2: Join Group Flow
1. First, create a test group (see below)
2. Dial USSD code
3. Enter `1` (Join Group)
4. Enter your group code
5. Should see success message

### Test 3: Payment Flow
1. Join a group first
2. Dial USSD code
3. Enter `2` (Pay Contribution)
4. Select your group
5. Should see payment confirmation

### Test 4: Payout Info
1. Join a group first
2. Dial USSD code
3. Enter `4` (My Payout Date)
4. Should see your position and payout schedule

---

## 🎨 Creating Test Data

Before testing payments, create a test group:

### Option 1: Using API (via Swagger UI)

1. Go to http://localhost:8000/docs
2. Register a user: `POST /auth/register`
   ```json
   {
     "phone_number": "+256700000001",
     "name": "Test User",
     "password": "password123"
   }
   ```
3. Login: `POST /auth/login`
4. Copy the access token
5. Click **Authorize** and paste token
6. Create group: `POST /groups/`
   ```json
   {
     "name": "Test Group",
     "contribution_amount": 50,
     "num_cycles": 10,
     "frequency": "MONTHLY"
   }
   ```
7. Note the `group_code` from response

### Option 2: Using curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700000001",
    "name": "Test User",
    "password": "password123"
  }'

# Login (save the token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700000001",
    "password": "password123"
  }'

# Create group (replace YOUR_TOKEN)
curl -X POST http://localhost:8000/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Family Savings",
    "contribution_amount": 50,
    "num_cycles": 10,
    "frequency": "MONTHLY"
  }'
```

---

## 🚀 Next Steps

Now that you have USSD working:

1. **Test all flows** thoroughly
2. **Enable SMS** (set `ENABLE_REAL_SMS=True` in `.env`)
3. **Add more features** to the USSD menu
4. **Prepare for production:**
   - Apply for production USSD code
   - Deploy to a production server
   - Set up monitoring
5. **Go live!** 🎉

---

## 📚 More Resources

### Quick References
- **Quick Ref Card:** [AFRICASTALKING_QUICKREF.md](AFRICASTALKING_QUICKREF.md)
- **Full Setup:** [backend/docs/AFRICASTALKING_SETUP.md](backend/docs/AFRICASTALKING_SETUP.md)
- **Integration Summary:** [AFRICASTALKING_INTEGRATION_SUMMARY.md](AFRICASTALKING_INTEGRATION_SUMMARY.md)

### Testing
- **Checklist:** [backend/AFRICASTALKING_CHECKLIST.md](backend/AFRICASTALKING_CHECKLIST.md)
- **Test Script:** `backend/test_africastalking_ussd.py`
- **curl Tests:** `backend/test_ussd_curl.sh`

### AfricaTalking
- **Dashboard:** https://account.africastalking.com/
- **Documentation:** https://developers.africastalking.com/docs/ussd
- **Support:** support@africastalking.com

---

## 💡 Pro Tips

1. **Keep ngrok running:** Each restart = new URL = update AT dashboard
2. **Use web simulator:** Faster than typing on phone during development
3. **Check logs:** Terminal output shows all USSD requests
4. **Test edge cases:** Invalid codes, timeouts, errors
5. **SMS costs money:** Keep `ENABLE_REAL_SMS=False` during development

---

## ❓ Need Help?

1. **Check troubleshooting** section above
2. **Read the docs** linked in this guide
3. **View backend logs** for error messages
4. **Test manually** with curl commands
5. **Check AT dashboard** → USSD → Logs

---

## 🎉 You're All Set!

You now have:
- ✅ Working USSD integration
- ✅ Local testing environment
- ✅ Complete documentation
- ✅ Testing tools
- ✅ Production-ready code

**Happy coding!** 🚀

Questions? Check the docs or open an issue on GitHub.

---

*Last updated: October 2025*

