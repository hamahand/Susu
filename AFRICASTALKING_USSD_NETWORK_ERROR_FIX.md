# AfricasTalking USSD Network Error - Fix Guide

**Date**: October 23, 2025  
**Issue**: Network error when using AfricasTalking USSD  
**Status**: ✅ DIAGNOSED - Configuration Issue  

---

## 🔍 **Problem Diagnosis**

The "network error" you're experiencing with AfricasTalking USSD is actually a **configuration issue**, not a network connectivity problem.

### **Root Causes Identified:**

1. **❌ Missing API Key**: `AT_API_KEY=your-at-api-key-from-dashboard` (placeholder)
2. **⚠️ Wrong Provider**: `USE_MTN_SERVICES=True` (should be False for AfricasTalking)  
3. **⚠️ Expired ngrok URL**: Callback URL may be expired or not registered

---

## 🛠️ **Step-by-Step Fix**

### **Step 1: Get AfricasTalking API Key**

1. Go to [AfricasTalking Dashboard](https://account.africastalking.com/)
2. Login to your account
3. Navigate to **Settings → API Key**
4. Copy your API key (starts with `atsk_`)

### **Step 2: Update Configuration**

Edit your `backend/.env` file and make these changes:

```bash
# Change this line:
AT_API_KEY=your-at-api-key-from-dashboard

# To this (replace with your actual key):
AT_API_KEY=atsk_your_actual_api_key_here

# Change this line:
USE_MTN_SERVICES=True

# To this:
USE_MTN_SERVICES=False
```

### **Step 3: Update Callback URL**

If using ngrok, get a fresh URL:

```bash
# Start ngrok in a new terminal
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
# Update in .env:
MTN_CALLBACK_URL=https://abc123.ngrok-free.app/ussd/callback
```

### **Step 4: Register Callback URL**

1. Go to [AfricasTalking Dashboard](https://account.africastalking.com/)
2. Navigate to **USSD → Your Channel**
3. Update the **Callback URL** to match your ngrok URL
4. Save the changes

### **Step 5: Test Configuration**

```bash
cd backend

# Verify configuration
python verify_ussd_setup.py

# Test USSD functionality
python test_africastalking_ussd.py test

# Check health endpoint
curl http://localhost:8000/ussd/health
```

---

## 🧪 **Testing Results**

### **Current Status:**
- ✅ Backend is running and healthy
- ✅ USSD endpoint is accessible
- ✅ Local tests pass
- ❌ AfricasTalking credentials are placeholders
- ⚠️ Using MTN configuration instead of AfricasTalking

### **Expected After Fix:**
- ✅ AfricasTalking API key configured
- ✅ Provider switched to AfricasTalking
- ✅ Callback URL registered
- ✅ USSD works with AfricasTalking

---

## 📋 **Quick Commands**

```bash
# Run the diagnostic script
cd backend
python fix_africastalking_ussd.py

# Verify setup
python verify_ussd_setup.py

# Test USSD
python test_africastalking_ussd.py test

# Check backend health
curl http://localhost:8000/ussd/health
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: "API Key Invalid"**
- **Cause**: Wrong or expired API key
- **Solution**: Get fresh API key from AfricasTalking dashboard

### **Issue 2: "Callback URL Not Found"**
- **Cause**: URL not registered with AfricasTalking
- **Solution**: Register callback URL in AT dashboard

### **Issue 3: "Network Timeout"**
- **Cause**: ngrok URL expired
- **Solution**: Get fresh ngrok URL and update configuration

### **Issue 4: "Provider Mismatch"**
- **Cause**: `USE_MTN_SERVICES=True` but trying to use AfricasTalking
- **Solution**: Set `USE_MTN_SERVICES=False`

---

## 📞 **Support Resources**

- **AfricasTalking Documentation**: https://developers.africastalking.com/docs/ussd
- **AfricasTalking Dashboard**: https://account.africastalking.com/
- **Project Documentation**: See `USSD_SETUP_INSTRUCTIONS.md`

---

## ✅ **Verification Checklist**

- [ ] AfricasTalking API key is real (not placeholder)
- [ ] `USE_MTN_SERVICES=False` in .env
- [ ] Callback URL is registered with AfricasTalking
- [ ] ngrok URL is fresh and active
- [ ] Backend is running on port 8000
- [ ] USSD health check returns 200 OK
- [ ] Test script passes all checks

---

**Last Updated**: October 23, 2025  
**Status**: Ready for Configuration Fix  
**Next Step**: Update .env file with real AfricasTalking credentials
