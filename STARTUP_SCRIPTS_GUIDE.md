# 🚀 SusuSave Startup Scripts Guide

Two comprehensive startup scripts to launch your entire SusuSave ecosystem with one command!

## 📁 Files

- **`start-dev.sh`** - Development environment (hot reload, debugging)
- **`start-prod.sh`** - Production environment (optimized, multiple workers)

## 🎯 Quick Start

### Development Mode

```bash
cd /Users/maham/susu
./start-dev.sh
```

### Production Mode

```bash
cd /Users/maham/susu
./start-prod.sh
```

---

## 🔧 Development Mode (`start-dev.sh`)

### What It Does

Starts all services in development mode with:
- ✅ Port conflict detection & resolution
- ✅ Interactive port selection
- ✅ Hot reload for frontend & backend
- ✅ Detailed logging
- ✅ Easy debugging
- ✅ Single Ctrl+C to stop everything

### Services Started

| Service | Default Port | Description |
|---------|-------------|-------------|
| **Backend API** | 8000 | FastAPI with auto-reload |
| **Ngrok Tunnel** | 4040 | Public URL for USSD callbacks |
| **Landing Page** | 8080 | Static site (Python HTTP server) |
| **PWA Web App** | 3000 | React + Vite dev server |
| **Android Emulator** | - | Pixel 8 Pro (optional) |
| **Expo Dev Server** | 8081 | iOS & Android development |

### Features

1. **Port Conflict Handling**
   - Automatically detects if ports are in use
   - Offers 3 options:
     - Kill existing process
     - Choose different port
     - Skip that service

2. **Interactive Setup**
   - Choose which services to start
   - Skip Android emulator if not needed
   - Skip Expo if not doing mobile dev

3. **Environment Variables**
   - Automatically sets `EXPO_PUBLIC_API_URL`
   - Configures Android SDK paths
   - Sets proper development flags

4. **Logging**
   - All logs in `/tmp/susu_logs/`
   - Separate log file per service
   - Easy to debug issues

### Usage Example

```bash
./start-dev.sh

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    🚀 SusuSave Development Environment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 
# This script will start all development services:
#   📄 Landing Page (Python HTTP Server)
#   🌐 PWA Web App (React + Vite)
#   🔧 Backend API (FastAPI)
#   🌍 Ngrok Tunnel (for USSD callbacks)
#   📱 iOS Simulator (Expo)
#   🤖 Android Emulator (Expo)
#
# Press Enter to continue...
```

### Stopping Services

Simply press **Ctrl+C** in the terminal. The script will:
- Stop all background processes
- Kill the Android emulator
- Clean up PID files
- Exit gracefully

---

## 🏭 Production Mode (`start-prod.sh`)

### What It Does

Starts all services in production mode with:
- ✅ Optimized builds
- ✅ Multiple workers (Gunicorn)
- ✅ Production-ready servers
- ✅ Health checks
- ✅ Database migrations
- ✅ Comprehensive logging

### Services Started

| Service | Default Port | Production Setup |
|---------|-------------|------------------|
| **Backend API** | 8000 | Gunicorn with 4 workers |
| **Landing Page** | 80 | http-server with caching |
| **PWA Web App** | 3000 | Vite build served by http-server |

### Features

1. **Pre-flight Checks**
   - Verifies Python, Node.js, npm installed
   - Checks all dependencies
   - Validates environment

2. **Database Migrations**
   - Runs `alembic upgrade head` automatically
   - Ensures database schema is up-to-date

3. **Production Builds**
   - PWA built with `npm run build`
   - Minified and optimized assets
   - Production environment variables

4. **Multi-Worker Backend**
   - 4 Gunicorn workers
   - Uvicorn worker class
   - Better performance & reliability
   - Timeout & keep-alive configured

5. **Health Monitoring**
   - Checks services every 60 seconds
   - Alerts if services fail
   - Logs health check status

6. **Enhanced Logging**
   - Logs in `/var/log/susu/`
   - Separate access & error logs
   - Log rotation ready

### Requirements

Install production dependencies:

```bash
# Backend
cd backend
pip install gunicorn

# Frontend (for better static serving)
npm install -g http-server
```

### Usage Example

```bash
./start-prod.sh

# Follow prompts for:
# - Port conflicts
# - Ngrok tunnel (optional for testing)
# - Service confirmations
```

---

## 🔍 Port Reference

### Default Ports

```
8000  - Backend API
8080  - Landing Page (dev) / 80 (prod)
3000  - PWA Web App
8081  - Expo Dev Server
4040  - Ngrok Dashboard
5554  - Android Emulator (ADB)
```

### Changing Ports

Both scripts detect port conflicts and allow you to:
1. Kill the conflicting process
2. Choose a different port
3. Skip that service

---

## 📝 Logs

### Development Logs

```bash
# Location
/tmp/susu_logs/

# Files
backend.log    - Backend API output
ngrok.log      - Ngrok tunnel output
landing.log    - Landing page server
pwa.log        - PWA dev server
emulator.log   - Android emulator output
```

### Production Logs

```bash
# Location
/var/log/susu/

# Files
backend.log          - Gunicorn output
backend-access.log   - API access logs
backend-error.log    - API error logs
landing.log          - Landing page server
pwa.log              - PWA server
pwa-build.log        - Build output
```

### Viewing Logs

```bash
# Tail logs in real-time
tail -f /tmp/susu_logs/backend.log

# View all logs
ls -la /tmp/susu_logs/

# Search for errors
grep -i error /tmp/susu_logs/*.log
```

---

## 🌐 Ngrok Integration

### What Ngrok Does

Ngrok creates a secure tunnel to your local backend, giving you a public URL like:
```
https://abc123def456.ngrok.io
```

### Why You Need It

- **USSD Callbacks**: AfricaTalking needs a public URL
- **Testing**: Test on real devices outside your network
- **Webhooks**: Receive webhooks from external services

### AfricaTalking Setup

1. Start the dev script (Ngrok starts automatically)
2. Copy the Ngrok URL from the output
3. Update AfricaTalking USSD callback:
   ```
   https://your-ngrok-url.ngrok.io/ussd/callback
   ```

### Ngrok Dashboard

Access at: http://localhost:4040
- View all requests
- Replay requests
- Inspect payloads

---

## 📱 Mobile Development

### iOS Development

1. Start dev script
2. When prompted for Expo, press `y`
3. Press `i` in Expo terminal to open iOS Simulator
4. App opens automatically

### Android Development

1. Start dev script
2. When prompted for Android emulator, press `y`
3. Wait for emulator to boot
4. When prompted for Expo, press `y`
5. Press `a` in Expo terminal to deploy to Android

### Environment Variables

The script automatically sets:
```bash
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
```

To use a different backend:
```bash
export EXPO_PUBLIC_API_URL=https://your-api.com
./start-dev.sh
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Problem**: Port is occupied

**Solution**: The script will ask you to:
1. Kill the process
2. Choose different port
3. Skip the service

Manual fix:
```bash
# Find process on port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)
```

### Android Emulator Won't Start

**Problem**: Emulator quits immediately

**Solution**: Check environment variables
```bash
# Verify in a new terminal
echo $ANDROID_SDK_ROOT
# Should show: /Users/maham/Library/Android/sdk

# If not, reload shell
source ~/.zshrc
```

### Backend Fails to Start

**Problem**: API doesn't respond

**Solution**: Check logs
```bash
tail -f /tmp/susu_logs/backend.log

# Check for:
# - Missing dependencies
# - Database connection errors
# - Port conflicts
```

### PWA Build Fails

**Problem**: Build errors

**Solution**:
```bash
cd web/app
rm -rf node_modules dist
npm install
npm run build
```

### Ngrok Fails

**Problem**: No tunnel URL

**Solution**:
```bash
# Check if ngrok is installed
which ngrok

# If not, install from https://ngrok.com/
# Or with Homebrew:
brew install ngrok

# Authenticate
ngrok authtoken YOUR_TOKEN
```

---

## 🎨 Customization

### Modify Default Ports

Edit the scripts:

```bash
# In start-dev.sh or start-prod.sh
LANDING_PORT=8080    # Change to your preferred port
PWA_PORT=3000        # Change to your preferred port
BACKEND_PORT=8000    # Change to your preferred port
```

### Skip Services

Comment out sections in the script:

```bash
# Comment out entire sections like:
# ============================================
# 3. Check and Start Landing Page
# ============================================
# ... entire section ...
```

### Add Custom Services

Add new sections following the pattern:

```bash
# ============================================
# 7. Your Custom Service
# ============================================
print_header "7️⃣  Your Service"

# Your service startup code here
```

---

## 📊 Service Status

### Check Running Services

```bash
# View all PIDs
cat /tmp/susu_dev_pids.txt

# Check if process is running
ps aux | grep -E "uvicorn|vite|python.*8080"

# Check specific ports
lsof -i :8000  # Backend
lsof -i :3000  # PWA
lsof -i :8080  # Landing
```

### Service Info File

Production mode saves info to:
```bash
cat /var/tmp/susu_services.txt
```

---

## 🔐 Security Notes

### Development Mode
- ✅ Safe for local development
- ⚠️  Never expose dev server publicly
- ⚠️  Uses `--localhost` flag for Expo

### Production Mode
- ⚠️  Review security settings before deploying
- ⚠️  Use proper SSL certificates
- ⚠️  Set strong passwords
- ⚠️  Configure firewall rules
- ⚠️  Use environment variables for secrets

---

## 🚦 Workflow Examples

### Full Stack Development

```bash
# Morning: Start everything
./start-dev.sh

# Work on features
# - Backend changes auto-reload
# - Frontend changes hot-reload
# - Mobile app updates on save

# Evening: Stop everything
# Press Ctrl+C
```

### Frontend Only

```bash
./start-dev.sh

# Skip backend when prompted
# Skip Android when prompted
# Skip Expo when prompted

# Only Landing & PWA will start
```

### Mobile Only

```bash
./start-dev.sh

# Skip Landing when prompted
# Skip PWA when prompted
# Start Android: y
# Start Expo: y

# Only Backend, Android, and Expo start
```

### Production Deployment

```bash
# Test locally first
./start-prod.sh

# Verify all services
# Check logs
# Test functionality

# Then deploy to server
```

---

## 📚 Additional Resources

- [Expo Documentation](https://docs.expo.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Android Emulator Guide](./mobile/SusuSaveMobile/ANDROID_EMULATOR_SETUP.md)

---

## 🆘 Need Help?

Check logs first:
```bash
# Development
ls -la /tmp/susu_logs/
tail -f /tmp/susu_logs/*.log

# Production
ls -la /var/log/susu/
tail -f /var/log/susu/*.log
```

Common issues:
1. Port conflicts → Let script handle it
2. Missing dependencies → Run npm/pip install
3. Emulator issues → Check Android SDK path
4. Build failures → Clear caches and rebuild

---

## 🎉 Success!

When everything works, you should see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎉 Development Environment Ready!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Services Running:

✓ Backend API:      http://localhost:8000
✓ API Docs:         http://localhost:8000/docs
✓ Ngrok Tunnel:     https://abc123.ngrok.io
✓ Ngrok Dashboard:  http://localhost:4040
✓ Landing Page:     http://localhost:8080
✓ PWA Web App:      http://localhost:3000
✓ Android Emulator: Running (Pixel 8 Pro)

Logs are available in: /tmp/susu_logs

⚠️  Press Ctrl+C to stop all services
```

Happy coding! 🚀


