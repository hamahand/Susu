# ⚡ SusuSave Quick Start - One Command

## 🎯 TL;DR

```bash
# Development (with hot reload)
cd /Users/maham/susu && ./start-dev.sh

# Production (optimized)
cd /Users/maham/susu && ./start-prod.sh
```

That's it! Everything starts automatically! 🚀

---

## 📦 One-Time Setup

### 1. Install Required Tools

```bash
# Install ngrok (for USSD callbacks)
brew install ngrok

# Install http-server (better static serving)
npm install -g http-server

# Install gunicorn (production backend)
cd backend
source venv/bin/activate
pip install gunicorn
```

### 2. Setup Environment

```bash
# Already done! Your .zshrc is configured ✅
# Android SDK paths are set
# Everything is ready to go
```

---

## 🚀 Usage

### Development Mode

```bash
./start-dev.sh
```

**What happens:**
1. Checks all ports
2. Starts Backend API (port 8000)
3. Starts Ngrok tunnel (gets public URL)
4. Starts Landing Page (port 8080)
5. Starts PWA Web App (port 3000)
6. Asks if you want Android emulator
7. Asks if you want Expo (iOS/Android)
8. Displays all URLs and info

**Interactive:**
- Choose which services to start
- Resolve port conflicts
- Skip services you don't need

**Perfect for:**
- Daily development
- Testing features
- Mobile app development
- USSD integration testing

### Production Mode

```bash
./start-prod.sh
```

**What happens:**
1. Pre-flight checks (Python, Node, npm)
2. Runs database migrations
3. Builds PWA (optimized)
4. Starts Backend with 4 workers
5. Serves static sites with caching
6. Enables health monitoring
7. Sets up production logging

**Perfect for:**
- Local production testing
- Performance testing
- Pre-deployment validation
- Staging environment

---

## 🎮 Quick Commands

### Start Everything (Dev)
```bash
./start-dev.sh
# Press Enter when prompted
# Answer 'y' for Android and Expo if needed
```

### Start Only Web (No Mobile)
```bash
./start-dev.sh
# Press Enter
# Answer 'n' for Android and Expo
```

### Stop Everything
```bash
# Press Ctrl+C in the terminal
# Script stops all services automatically
```

### View Logs
```bash
# Development
tail -f /tmp/susu_logs/backend.log

# Production
tail -f /var/log/susu/backend.log
```

### Check What's Running
```bash
# View URLs and status
cat /var/tmp/susu_services.txt

# Check ports
lsof -i :8000  # Backend
lsof -i :3000  # PWA
lsof -i :8080  # Landing
```

---

## 📱 Access Your Apps

### After Starting Dev Mode:

| Service | URL | Notes |
|---------|-----|-------|
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Landing Page** | http://localhost:8080 | Marketing site |
| **PWA Web App** | http://localhost:3000 | Main app |
| **Ngrok Tunnel** | https://[random].ngrok.io | Public URL |
| **Ngrok Dashboard** | http://localhost:4040 | Inspect requests |
| **Expo** | http://localhost:8081 | Mobile dev |

### For Mobile Development:

**iOS:**
1. Start dev script
2. When Expo prompt appears, press `i`
3. iOS Simulator opens automatically

**Android:**
1. Start dev script
2. Say 'y' to Android emulator
3. Say 'y' to Expo
4. Press `a` to deploy to Android

---

## 🔧 Port Conflicts?

**No problem!** The script handles it:

```
⚠️  Port 8000 is in use by another process

Options:
  1. Kill the existing process and use port 8000
  2. Choose a different port
  3. Skip starting Backend API

Choose option (1/2/3): 
```

Choose what works for you!

---

## 🌐 USSD Integration

**Automatic with Ngrok:**

1. Start dev script
2. Copy the Ngrok URL from output
3. Update AfricaTalking:
   ```
   https://your-url.ngrok.io/ussd/callback
   ```
4. Test immediately!

**View all USSD requests:**
- Go to http://localhost:4040
- See every request in real-time
- Replay requests for testing

---

## 🐛 Troubleshooting

### "Port already in use"
✅ Script will offer to kill it or choose another port

### "Android emulator quits"
✅ Already fixed! Your .zshrc is configured

### "Ngrok not found"
```bash
brew install ngrok
```

### "Backend won't start"
```bash
# Check logs
tail -f /tmp/susu_logs/backend.log

# Try manually
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### "PWA won't build"
```bash
cd web/app
rm -rf node_modules
npm install
npm run dev
```

### Need to reset everything?
```bash
# Kill all processes
pkill -f "uvicorn|vite|http.server|expo|ngrok"

# Kill emulator
pkill -f "emulator @Pixel_8_Pro"

# Clear PIDs
rm /tmp/susu_dev_pids.txt

# Start fresh
./start-dev.sh
```

---

## 💡 Pro Tips

### Tip 1: Keep Emulator Running
Once Android emulator boots, keep it running all day. Subsequent starts are instant!

### Tip 2: Use Production Mode for Testing
Test production builds locally before deploying:
```bash
./start-prod.sh
```

### Tip 3: Monitor All Logs
```bash
# Open multiple terminals
tail -f /tmp/susu_logs/backend.log
tail -f /tmp/susu_logs/pwa.log
tail -f /tmp/susu_logs/ngrok.log
```

### Tip 4: Custom Ports
Edit the scripts if you prefer different default ports:
```bash
# In start-dev.sh
LANDING_PORT=8080
PWA_PORT=3000
BACKEND_PORT=8000
```

### Tip 5: Skip Services
Don't need something? Just answer 'n' or choose option 3 when prompted!

---

## 📋 Cheat Sheet

```bash
# Start development
./start-dev.sh

# Start production
./start-prod.sh

# Stop everything
# Press Ctrl+C

# View logs (dev)
ls /tmp/susu_logs/

# View logs (prod)
ls /var/log/susu/

# Check running services
cat /var/tmp/susu_services.txt

# Check ports
lsof -i :8000
lsof -i :3000
lsof -i :8080

# Android emulator
adb devices

# Kill a port
kill -9 $(lsof -ti:8000)

# View ngrok dashboard
open http://localhost:4040
```

---

## 🎯 Workflow Examples

### Full Stack Dev Day

```bash
# Morning
cd /Users/maham/susu
./start-dev.sh

# Work all day
# - Code updates auto-reload
# - Test on emulator/simulator
# - Debug with logs

# Evening
# Press Ctrl+C to stop
```

### Mobile-Only Dev

```bash
./start-dev.sh
# Skip Landing: 3
# Skip PWA: 3
# Android: y
# Expo: y

# Now: Backend + Mobile only
```

### Quick API Test

```bash
./start-dev.sh
# Skip Landing: 3
# Skip PWA: 3
# Skip Android: n
# Skip Expo: n

# Now: Just Backend + Ngrok
```

---

## ✨ What Makes This Special?

✅ **One Command** - Start everything instantly
✅ **Smart Port Handling** - No more port conflicts
✅ **Interactive** - Choose what you need
✅ **Safe Cleanup** - Ctrl+C stops everything
✅ **Great Logging** - Easy debugging
✅ **Production Ready** - Test before deploy
✅ **Mobile Support** - iOS & Android integrated
✅ **USSD Ready** - Ngrok auto-configured

---

## 🎉 You're Ready!

```bash
cd /Users/maham/susu
./start-dev.sh
```

The future of savings starts now! 🚀💰

---

**Need more details?** → See [STARTUP_SCRIPTS_GUIDE.md](./STARTUP_SCRIPTS_GUIDE.md)

**Android issues?** → See [mobile/SusuSaveMobile/ANDROID_EMULATOR_SETUP.md](./mobile/SusuSaveMobile/ANDROID_EMULATOR_SETUP.md)

**General setup?** → See [START_HERE.md](./START_HERE.md)


