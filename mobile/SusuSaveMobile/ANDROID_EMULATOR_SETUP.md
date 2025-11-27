# Android Emulator Setup - Fixed! ✅

## What Was Fixed

Your Android emulator wasn't working because of conflicting environment variables in `~/.zshrc`:
- ❌ `ANDROID_HOME` was pointing to `/opt/homebrew/share/android-commandlinetools` (Homebrew CLI tools)
- ✅ Fixed to point to `$HOME/Library/Android/sdk` (actual Android Studio SDK)

## Your Environment Variables (now set correctly)

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
export PATH="$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"
```

## Quick Start

### Option 1: Use the Startup Script (Easiest!)

```bash
cd /Users/maham/susu/mobile/SusuSaveMobile
./start-android.sh
```

This script will:
1. Check if emulator is running
2. Start it if needed
3. Wait for it to fully boot
4. Launch Expo dev server
5. Open your app on Android

### Option 2: Manual Commands

**Start the emulator:**
```bash
$ANDROID_SDK_ROOT/emulator/emulator @Pixel_8_Pro &
```

**Wait for it to boot, then start Expo:**
```bash
cd /Users/maham/susu/mobile/SusuSaveMobile
npx expo start --android
```

## Important Notes

1. **First Boot**: The emulator takes 1-2 minutes to fully boot the first time
2. **Keep Running**: Once booted, keep the emulator running for faster development
3. **New Terminal**: If you open a new terminal, the environment variables will be automatically loaded from `~/.zshrc`
4. **Old Terminal**: If using an existing terminal, run: `source ~/.zshrc`

## Verify Setup

Check if emulator is running:
```bash
adb devices
```

Should show:
```
List of devices attached
emulator-5554    device
```

## Your Emulator Details

- **AVD Name**: Pixel_8_Pro
- **Serial**: emulator-5554
- **Resolution**: 1344x2992
- **API Level**: 36 (Android 15)
- **Architecture**: arm64-v8a (Apple Silicon native)

## Troubleshooting

If you still have issues:

1. **Kill all emulator processes:**
   ```bash
   pkill -9 qemu-system
   ```

2. **Restart with verbose logging:**
   ```bash
   $ANDROID_SDK_ROOT/emulator/emulator @Pixel_8_Pro -verbose
   ```

3. **Check logs:**
   ```bash
   tail -f /tmp/emulator.log
   ```

## Development Workflow

1. Start emulator (only once per day):
   ```bash
   ./start-android.sh
   ```

2. Press `a` in Expo terminal to deploy to Android

3. Code changes will hot-reload automatically 🔥

4. Press `r` in Expo terminal to manually reload

Happy coding! 🎉


