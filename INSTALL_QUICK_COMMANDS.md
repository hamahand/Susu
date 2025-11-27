# 🎯 Install SusuSave Quick Commands

Transform your workflow with simple commands like `susu-dev` and `susu-prod`!

## 🚀 One-Line Installation

```bash
echo 'source /Users/maham/susu/.susu_aliases' >> ~/.zshrc && source ~/.zshrc
```

Done! ✅

---

## 📋 What You Get

After installation, you can use these commands from **anywhere**:

### Start Services
```bash
susu-dev          # Start development environment
susu-prod         # Start production environment
susu-stop         # Stop all services
```

### View Logs
```bash
susu-logs         # List all log files
susu-log-backend  # Watch backend log
susu-log-pwa      # Watch PWA log
susu-log-ngrok    # Watch ngrok log
```

### Check Status
```bash
susu-status       # Show all running services
susu-ports        # Check which ports are in use
susu-ngrok        # Get ngrok public URL
```

### Android
```bash
susu-android      # Start Android emulator
susu-adb          # List Android devices
```

### Quick Navigation
```bash
susu              # Go to /Users/maham/susu
susu-backend      # Go to backend folder
susu-web          # Go to web folder
susu-mobile       # Go to mobile folder
```

### Ngrok
```bash
susu-ngrok-dash   # Open ngrok dashboard in browser
```

### Help
```bash
susu-help         # Show all commands
```

---

## 💡 Usage Examples

### Example 1: Start Development

```bash
# From anywhere in your system:
susu-dev

# That's it! Everything starts automatically
```

### Example 2: Check Status

```bash
# Check if services are running
susu-status

# Output:
# SusuSave Production Services
# Started: Mon Oct 22 09:30:00 PDT 2025
# Backend API: http://localhost:8000
# Landing Page: http://localhost:8080
# PWA Web App: http://localhost:3000
```

### Example 3: View Logs

```bash
# Watch backend logs in real-time
susu-log-backend

# In another terminal, watch PWA logs
susu-log-pwa
```

### Example 4: Get Ngrok URL

```bash
# Get public URL for USSD callbacks
susu-ngrok

# Output: https://abc123def456.ngrok.io
```

### Example 5: Quick Navigation

```bash
# Jump to mobile project
susu-mobile

# You're now at: /Users/maham/susu/mobile/SusuSaveMobile
```

---

## 🔧 Manual Installation (Step by Step)

If you prefer to install manually:

### Step 1: Edit .zshrc

```bash
nano ~/.zshrc
```

### Step 2: Add This Line

Add at the end of the file:

```bash
# SusuSave Quick Commands
source /Users/maham/susu/.susu_aliases
```

### Step 3: Save and Reload

Press `Ctrl+X`, then `Y`, then `Enter`

```bash
source ~/.zshrc
```

### Step 4: Test

```bash
susu-help
```

You should see the help menu! ✅

---

## 🎨 Customization

### Add Your Own Aliases

Edit the aliases file:

```bash
nano /Users/maham/susu/.susu_aliases
```

Add custom aliases:

```bash
# Your custom aliases
alias susu-test='cd /Users/maham/susu/backend && pytest'
alias susu-migrate='cd /Users/maham/susu/backend && alembic upgrade head'
alias susu-seed='cd /Users/maham/susu/backend && python seed_data.py'
```

Save and reload:

```bash
source ~/.zshrc
```

---

## 🔍 What's Included

The aliases file provides:

1. **Service Management** - Start/stop services easily
2. **Log Viewing** - Quick access to all logs
3. **Status Checking** - See what's running
4. **Port Monitoring** - Check port usage
5. **Navigation** - Jump between folders
6. **Android Tools** - Emulator and ADB shortcuts
7. **Ngrok Helpers** - Get URLs and open dashboard
8. **Help System** - Built-in documentation

---

## ❓ Troubleshooting

### Commands Not Found

```bash
# Reload your shell configuration
source ~/.zshrc

# Verify the alias file exists
ls -la /Users/maham/susu/.susu_aliases

# Check if it's loaded
alias | grep susu
```

### Wrong Path

If you moved the susu folder:

```bash
# Edit the aliases file
nano /Users/maham/susu/.susu_aliases

# Update the paths to match your location
# Save and reload
source ~/.zshrc
```

### Conflicts with Existing Aliases

```bash
# Check existing aliases
alias | grep susu

# If conflicts exist, edit .susu_aliases
# Rename conflicting commands
nano /Users/maham/susu/.susu_aliases
```

---

## 🎯 Quick Reference Card

```bash
# Services
susu-dev          # Start all (development)
susu-prod         # Start all (production)
susu-stop         # Stop all

# Logs
susu-logs         # List logs
susu-log-backend  # Backend log
susu-log-pwa      # PWA log

# Status
susu-status       # Service status
susu-ports        # Port usage
susu-ngrok        # Ngrok URL

# Navigate
susu              # Project root
susu-backend      # Backend folder
susu-web          # Web folder
susu-mobile       # Mobile folder

# Help
susu-help         # Show all commands
```

---

## 🎉 Benefits

### Before Installation:
```bash
cd /Users/maham/susu
./start-dev.sh
cd backend
tail -f /tmp/susu_logs/backend.log
```

### After Installation:
```bash
susu-dev
susu-log-backend
```

**Much faster!** 🚀

---

## 🔄 Uninstall

To remove the aliases:

```bash
# Edit .zshrc
nano ~/.zshrc

# Remove or comment out this line:
# source /Users/maham/susu/.susu_aliases

# Reload
source ~/.zshrc
```

The aliases will be removed from new terminal sessions.

---

## 📚 Next Steps

1. **Install the aliases:**
   ```bash
   echo 'source /Users/maham/susu/.susu_aliases' >> ~/.zshrc && source ~/.zshrc
   ```

2. **Test it:**
   ```bash
   susu-help
   ```

3. **Start developing:**
   ```bash
   susu-dev
   ```

4. **Explore the guides:**
   - [Quick Start All](./QUICK_START_ALL.md)
   - [Startup Scripts Guide](./STARTUP_SCRIPTS_GUIDE.md)
   - [Android Emulator Setup](./mobile/SusuSaveMobile/ANDROID_EMULATOR_SETUP.md)

---

**Ready to supercharge your workflow?** 🚀

```bash
echo 'source /Users/maham/susu/.susu_aliases' >> ~/.zshrc && source ~/.zshrc && susu-help
```


