#!/bin/bash

# Android Emulator and Expo Startup Script
# This script starts the Android emulator and launches the Expo app

set -e

echo "🚀 Starting Android Emulator..."

# Set Android environment variables
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
export PATH="$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"

# Check if emulator is already running
EMULATOR_RUNNING=$(adb devices | grep "emulator-" | grep "device" || true)

if [ -z "$EMULATOR_RUNNING" ]; then
    echo "📱 Launching Pixel 8 Pro emulator..."
    nohup $ANDROID_SDK_ROOT/emulator/emulator @Pixel_8_Pro -no-snapshot-load > /tmp/emulator.log 2>&1 &
    
    echo "⏳ Waiting for emulator to boot (this may take 1-2 minutes)..."
    adb wait-for-device
    
    # Wait for boot to complete
    while [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; do
        echo "   Still booting..."
        sleep 2
    done
    
    echo "✅ Emulator is ready!"
else
    echo "✅ Emulator is already running"
fi

# Start Expo
echo "🎨 Starting Expo development server..."
echo ""
echo "Press 'a' to open the app on Android, or 'r' to reload"
echo ""

npx expo start

echo "👋 Goodbye!"


