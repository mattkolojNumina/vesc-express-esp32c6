#!/bin/bash
# Build release APK for VESC Tool Android app

cd /home/rds/vesc_express/vesc_tool

echo "🔧 Building VESC Tool release APK..."

# Clean previous build
rm -rf android-build/build/

# Build release APK using Qt's build system
if command -v qmake >/dev/null 2>&1; then
    echo "📱 Building with qmake..."
    
    # Set Android environment variables if needed
    export ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-/opt/android-sdk}
    export ANDROID_NDK_ROOT=${ANDROID_NDK_ROOT:-/opt/android-ndk}
    
    # Build the project
    mkdir -p build-android
    cd build-android
    
    qmake ../vesc_tool.pro -spec android-clang CONFIG+=release
    make -j$(nproc)
    make apk
    
    echo "✅ Release APK built successfully!"
    echo "📦 Location: $(find . -name '*.apk' -type f)"
    
else
    echo "❌ qmake not found. Install Qt for Android development."
    echo "💡 Alternative: Use Android Studio to build the project"
    echo "   1. Open vesc_tool/ directory in Android Studio"
    echo "   2. Build → Generate Signed Bundle/APK"
    echo "   3. Choose APK and create signing key"
fi