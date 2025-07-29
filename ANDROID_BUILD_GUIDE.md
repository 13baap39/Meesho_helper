# 🛠️ Android App Build Instructions

This guide explains how to build the Meesho Helper Android app from source code.

## 📋 Prerequisites

### Development Environment
- **Android Studio**: Latest version (Flamingo or newer)
- **Java JDK**: OpenJDK 11 or 17
- **Android SDK**: API levels 24-34
- **Gradle**: 8.4+ (included with Android Studio)
- **Git**: For cloning the repository

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 10GB free space for Android SDK and project

## 🚀 Setup Instructions

### 1. Install Android Studio

#### Windows
1. Download Android Studio from https://developer.android.com/studio
2. Run the installer and follow setup wizard
3. Install recommended SDK components

#### macOS
1. Download Android Studio DMG
2. Drag to Applications folder
3. Launch and complete setup

#### Linux
1. Download tar.gz file
2. Extract and run `studio.sh`
3. Follow setup wizard

### 2. Configure Android SDK

1. Open Android Studio
2. Go to `Tools > SDK Manager`
3. Install required components:
   - Android SDK Platform 24 (minimum)
   - Android SDK Platform 34 (target)
   - Android SDK Build-Tools 34.0.0
   - Android SDK Platform-Tools
   - Android SDK Tools

### 3. Clone Repository

```bash
git clone https://github.com/13baap39/Meesho_helper.git
cd Meesho_helper/android-app
```

## 🔧 Building the Project

### Method 1: Using Android Studio (Recommended)

1. **Open Project**
   - Launch Android Studio
   - Select "Open an existing project"
   - Navigate to `Meesho_helper/android-app`
   - Click "OK"

2. **Gradle Sync**
   - Wait for Gradle sync to complete
   - If sync fails, check internet connection and retry

3. **Build Debug APK**
   - Go to `Build > Build Bundle(s) / APK(s) > Build APK(s)`
   - Wait for build to complete
   - APK will be in `app/build/outputs/apk/debug/`

4. **Build Release APK**
   - Go to `Build > Generate Signed Bundle / APK`
   - Select "APK" and click "Next"
   - Create or select signing key
   - Choose "release" build variant
   - Click "Finish"

### Method 2: Using Command Line

1. **Navigate to Project**
   ```bash
   cd Meesho_helper/android-app
   ```

2. **Make Gradlew Executable**
   ```bash
   chmod +x gradlew
   ```

3. **Build Debug APK**
   ```bash
   ./gradlew assembleDebug
   ```

4. **Build Release APK**
   ```bash
   ./gradlew assembleRelease
   ```

## 📱 Testing on Device

### 1. Enable Developer Options
1. Go to Settings > About Phone
2. Tap "Build Number" 7 times
3. Go back to Settings > Developer Options
4. Enable "USB Debugging"

### 2. Connect Device
1. Connect Android device via USB
2. Accept USB debugging prompt on device
3. Device should appear in Android Studio

### 3. Run App
1. Click "Run" button (green triangle) in Android Studio
2. Select your device from the list
3. App will be installed and launched

## 🔍 Project Structure

```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/meeshohelper/
│   │   │   ├── MainActivity.java              # Main app entry point
│   │   │   ├── activities/
│   │   │   │   ├── LeafletGeneratorActivity.java  # Leaflet generation
│   │   │   │   ├── BillCombinerActivity.java      # Bill combining
│   │   │   │   └── HybridBillActivity.java        # Hybrid bills
│   │   │   ├── utils/
│   │   │   │   ├── PDFProcessor.java              # Core PDF operations
│   │   │   │   ├── LeafletGenerator.java          # Leaflet creation
│   │   │   │   └── FileManager.java               # File operations
│   │   │   └── models/
│   │   │       └── CustomerData.java              # Data model
│   │   ├── res/
│   │   │   ├── layout/                            # XML layouts
│   │   │   ├── values/                            # Strings, colors, themes
│   │   │   ├── drawable/                          # Icons and graphics
│   │   │   └── mipmap-*/                          # App icons
│   │   └── AndroidManifest.xml                    # App configuration
│   ├── build.gradle                               # App build configuration
│   └── proguard-rules.pro                         # Code obfuscation rules
├── gradle/wrapper/                                # Gradle wrapper files
├── build.gradle                                   # Project build configuration
├── settings.gradle                                # Project settings
└── README.md                                      # Documentation
```

## 🧪 Testing

### Unit Tests
```bash
./gradlew test
```

### Instrumented Tests
```bash
./gradlew connectedAndroidTest
```

### Manual Testing Checklist
- [ ] App launches without crashes
- [ ] File picker opens and selects PDFs
- [ ] Leaflet generation works with sample PDF
- [ ] Bill combining processes correctly
- [ ] Hybrid bill generation completes
- [ ] Generated files can be downloaded/shared
- [ ] Permissions are handled properly

## 🏗️ Build Variants

### Debug Build
- **Purpose**: Development and testing
- **Features**: Debugging enabled, logging verbose
- **Signing**: Debug keystore (auto-generated)
- **Command**: `./gradlew assembleDebug`

### Release Build
- **Purpose**: Production deployment
- **Features**: Optimized, obfuscated code
- **Signing**: Release keystore (must be configured)
- **Command**: `./gradlew assembleRelease`

## 🔐 Signing Configuration

### For Release Builds
1. **Generate Keystore**
   ```bash
   keytool -genkey -v -keystore release-key.keystore -alias meesho-helper -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure in build.gradle**
   ```gradle
   android {
       signingConfigs {
           release {
               storeFile file('release-key.keystore')
               storePassword 'your-store-password'
               keyAlias 'meesho-helper'
               keyPassword 'your-key-password'
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
               // ... other settings
           }
       }
   }
   ```

## 🚨 Troubleshooting

### Common Build Issues

#### Gradle Sync Failed
- **Solution**: Check internet connection, update Gradle wrapper
- **Command**: `./gradlew wrapper --gradle-version 8.4`

#### SDK Not Found
- **Solution**: Set ANDROID_HOME environment variable
- **Linux/Mac**: `export ANDROID_HOME=$HOME/Android/Sdk`
- **Windows**: `set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk`

#### Build Tools Version
- **Error**: Build tools version not found
- **Solution**: Install required build tools via SDK Manager

#### Java Version Issues
- **Error**: Unsupported Java version
- **Solution**: Use JDK 11 or 17, set JAVA_HOME correctly

#### Dependency Resolution
- **Error**: Cannot resolve dependencies
- **Solution**: Check internet connection, clear Gradle cache
- **Command**: `./gradlew clean --refresh-dependencies`

### Memory Issues
If build fails due to memory:
```gradle
// In gradle.properties
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=512m
```

## 📦 Distribution

### APK Distribution
1. Build release APK
2. Test on multiple devices
3. Upload to distribution platform or share directly

### Google Play Store
1. Create app bundle: `./gradlew bundleRelease`
2. Upload AAB file to Play Console
3. Follow Play Store guidelines

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Android CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'temurin'
    - name: Cache Gradle packages
      uses: actions/cache@v2
      with:
        path: ~/.gradle/caches
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle') }}
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
      working-directory: ./android-app
    - name: Build with Gradle
      run: ./gradlew assembleDebug
      working-directory: ./android-app
```

## 📚 Additional Resources

### Documentation
- [Android Developer Guide](https://developer.android.com/guide)
- [iText 7 Documentation](https://itextpdf.com/en/resources/api-documentation)
- [Material Design Guidelines](https://material.io/design)

### Tools
- [APK Analyzer](https://developer.android.com/studio/build/apk-analyzer) - Analyze APK contents
- [Layout Inspector](https://developer.android.com/studio/debug/layout-inspector) - Debug UI layouts
- [Logcat](https://developer.android.com/studio/debug/am-logcat) - View app logs

---

*This build guide covers all aspects of compiling and distributing the Meesho Helper Android app. Follow these instructions carefully to ensure successful builds.*