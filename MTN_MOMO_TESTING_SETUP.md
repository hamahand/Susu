# 🧪 MTN MoMo Testing Setup - Complete Guide

**Date**: October 23, 2025  
**Reference**: [MTN MoMo Developer Testing Documentation](https://momodeveloper.mtn.com/api-documentation/testing)  
**Status**: ✅ Complete Testing Setup Guide

---

## 🎯 **MTN MoMo Sandbox Testing**

Based on the official MTN MoMo Developer documentation, here's the complete setup for testing your payment integration:

---

## 📋 **Step 1: MTN Developer Account Setup**

### **1.1 Create MTN Developer Account**
1. Go to [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Click "Sign up" to create an account
3. Verify your email address
4. Complete your profile setup

### **1.2 Create a New App**
1. Login to your MTN developer account
2. Navigate to "Products" → "MoMo API"
3. Click "Create New App"
4. Fill in app details:
   - **App Name**: SusuSave Payment App
   - **Description**: Payment integration for SusuSave groups
   - **Environment**: Sandbox (for testing)

---

## 🔑 **Step 2: Get API Credentials**

### **2.1 Get Subscription Key**
1. In your app dashboard, go to "API Keys"
2. Copy your **Primary Key** (subscription key)
3. This will be used in your backend configuration

### **2.2 Get Environment Details**
- **Sandbox Base URL**: `https://sandbox.momodeveloper.mtn.com`
- **Production Base URL**: `https://api.mtn.com` (for later production use)

---

## ⚙️ **Step 3: Configure Your Backend**

### **3.1 Update Backend Configuration**
```bash
cd /Users/maham/susu/backend

# Create or update .env file
cp env.example .env
```

### **3.2 Set Environment Variables**
Add these to your `backend/.env` file:
```bash
# MTN MoMo Configuration
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key_here
MTN_MOMO_ENVIRONMENT=sandbox
MTN_MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_API_USER_ID=your_api_user_id
MTN_MOMO_API_KEY=your_api_key

# Enable MTN MoMo
ENABLE_MTN_MOMO=true
```

### **3.3 Run Setup Script**
```bash
cd /Users/maham/susu/backend
python3 setup_mtn_momo.py
```

---

## 🌐 **Step 4: Set Up ngrok for Testing**

### **4.1 Install and Start ngrok**
```bash
# Install ngrok (if not already installed)
# Download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000
```

### **4.2 Copy ngrok URL**
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### **4.3 Update MTN Callback URL**
1. Go to your MTN app dashboard
2. Navigate to "Webhooks" or "Callback URLs"
3. Set callback URL to: `https://your-ngrok-url.ngrok.io/payments/momo/callback`

---

## 🧪 **Step 5: Test with MTN Sandbox**

### **5.1 Test Phone Numbers**
According to MTN documentation, use these test numbers:

**Auto-Approve Numbers:**
```
+233240000001 to +233240000099
```

**Auto-Reject Numbers:**
```
+233240000100 to +233240000199
```

### **5.2 Test Payment Flow**

#### **Run Test Script**
```bash
cd /Users/maham/susu/backend
python3 test_payment_flow.py
```

#### **Test with Mobile App**
```bash
cd /Users/maham/susu/mobile/SusuSaveMobile

# iOS
npm run ios

# Android
npm run android
```

#### **Test with Web App**
```bash
# Open browser
open http://localhost:5173
```

---

## 📱 **Step 6: Testing Scenarios**

### **6.1 User Payment Test**
1. Login to your app
2. Navigate to a group
3. Find your unpaid contribution
4. Tap "Pay Now"
5. Use test phone number (+233240000001)
6. Payment should auto-approve

### **6.2 Admin Request Test**
1. Login as group admin
2. Navigate to group dashboard
3. Find unpaid member
4. Tap "Request Payment"
5. Member receives MoMo prompt
6. Use test number for approval

### **6.3 Payment Status Check**
1. After payment attempt
2. Check payment status in app
3. Verify status updates to "Paid"
4. Check backend logs for MTN callbacks

---

## 🔍 **Step 7: Debugging & Monitoring**

### **7.1 Check Backend Logs**
```bash
cd /Users/maham/susu
docker logs sususave_backend --tail 50 --follow
```

### **7.2 Monitor ngrok Traffic**
1. Go to http://localhost:4040 (ngrok web interface)
2. Check incoming requests
3. Verify MTN callback requests

### **7.3 Check MTN Developer Dashboard**
1. Login to MTN developer portal
2. Check API usage and logs
3. Verify callback delivery

---

## 📊 **Step 8: Expected Test Results**

### **8.1 Successful Payment Flow**
```
1. User taps "Pay Now"
   ↓
2. Backend creates payment record
   ↓
3. MTN MoMo API called
   ↓
4. Test phone receives prompt
   ↓
5. Payment auto-approves
   ↓
6. MTN sends callback to backend
   ↓
7. Payment status updated to SUCCESS
   ↓
8. UI updates to show "Paid"
```

### **8.2 Log Output Examples**
```
✅ Payment request sent to MTN
✅ MTN callback received
✅ Payment status updated to SUCCESS
✅ User notified of successful payment
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Authentication Error**
**Error**: "Invalid subscription key"
**Solution**: 
- Verify subscription key in .env file
- Check MTN developer dashboard for correct key

### **Issue 2: Callback Not Received**
**Error**: No MTN callback received
**Solution**:
- Verify ngrok is running
- Check callback URL in MTN dashboard
- Ensure backend is accessible via ngrok

### **Issue 3: Payment Not Processing**
**Error**: Payment stuck in pending
**Solution**:
- Check phone number format (+233...)
- Verify test phone numbers
- Check backend logs for errors

### **Issue 4: App Not Updating**
**Error**: UI not showing payment status
**Solution**:
- Refresh the app
- Check if payment status endpoint is working
- Verify frontend-backend communication

---

## 📈 **Step 9: Production Preparation**

### **9.1 Switch to Production**
Once testing is complete:
1. Update environment variables:
   ```bash
   MTN_MOMO_ENVIRONMENT=production
   MTN_MOMO_BASE_URL=https://api.mtn.com
   ```
2. Get production subscription key
3. Update callback URL to production domain

### **9.2 Production Testing**
1. Test with real phone numbers
2. Monitor payment success rates
3. Set up error monitoring
4. Configure production logging

---

## ✅ **Testing Checklist**

- [ ] MTN developer account created
- [ ] App created in MTN dashboard
- [ ] Subscription key obtained
- [ ] Backend .env configured
- [ ] ngrok tunnel running
- [ ] Callback URL updated in MTN dashboard
- [ ] Test script runs successfully
- [ ] Mobile app payment flow works
- [ ] Web app payment flow works
- [ ] Payment status updates correctly
- [ ] MTN callbacks received
- [ ] Error handling works

---

## 🎯 **Quick Start Commands**

```bash
# 1. Start services
cd /Users/maham/susu
docker-compose up -d

# 2. Set up MTN credentials
cd backend
python3 setup_mtn_momo.py

# 3. Start ngrok
ngrok http 8000

# 4. Test payment flow
python3 test_payment_flow.py

# 5. Test mobile app
cd ../mobile/SusuSaveMobile
npm run ios    # or npm run android
```

---

## 📚 **Additional Resources**

- [MTN MoMo Developer Documentation](https://momodeveloper.mtn.com/api-documentation/testing)
- [MTN MoMo API Reference](https://momodeveloper.mtn.com/api-documentation)
- [MTN Developer Support](https://momodeveloper.mtn.com/support)

---

**Status**: ✅ Complete MTN MoMo Testing Setup Guide  
**Next**: Follow the steps above to complete your MTN MoMo integration testing

---

**Your MTN MoMo payment integration is ready for testing!** 🎉
