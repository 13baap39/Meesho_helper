# 📲 Meesho Helper Android App - Installation Guide

This guide will help you install and use the Meesho Helper Android app on your device.

## 📋 Prerequisites

### Device Requirements
- **Android Version**: Android 7.0 (API level 24) or higher
- **Storage**: At least 50MB of free space
- **RAM**: Minimum 2GB RAM recommended
- **Permissions**: Storage access permission required

### Recommended Apps
- **PDF Viewer**: Any PDF reader app (Adobe Acrobat, Google Drive, etc.)
- **File Manager**: For easy file navigation
- **WhatsApp**: For customer communication (as mentioned in leaflets)

## 🚀 Installation Methods

### Method 1: Install from APK (Recommended)

1. **Download APK**
   - Download the `MeeshoHelper.apk` file from the releases section
   - Save it to your device's Downloads folder

2. **Enable Unknown Sources**
   - Go to `Settings > Security > Unknown Sources`
   - Or `Settings > Apps > Special Access > Install Unknown Apps`
   - Enable installation from unknown sources for your browser/file manager

3. **Install the App**
   - Open your file manager and navigate to Downloads
   - Tap on `MeeshoHelper.apk`
   - Tap "Install" and wait for installation to complete
   - Tap "Open" to launch the app

### Method 2: Build from Source (For Developers)

1. **Install Android Studio**
   - Download and install Android Studio
   - Install Android SDK (API 24-34)
   - Install Java JDK 11 or higher

2. **Clone Repository**
   ```bash
   git clone https://github.com/13baap39/Meesho_helper.git
   cd Meesho_helper/android-app
   ```

3. **Open in Android Studio**
   - Open Android Studio
   - Select "Open an existing project"
   - Navigate to the `android-app` folder
   - Wait for Gradle sync to complete

4. **Build and Install**
   - Connect your Android device via USB
   - Enable Developer Options and USB Debugging
   - Click "Run" button in Android Studio
   - Select your device and install

## 🔑 First Time Setup

### 1. Launch the App
- Tap the Meesho Helper icon on your home screen
- The app will open to the main dashboard

### 2. Grant Permissions
- The app will request storage permissions
- Tap "Allow" to grant access to your files
- This is required to read PDF files and save generated outputs

### 3. Test the App
- Try uploading a small PDF file first
- Ensure all features work properly before processing important files

## 📱 Using the App

### Main Dashboard
The app has three main features accessible from the home screen:

1. **📄 Leaflet Generator** - Create thank-you leaflets from order labels
2. **📋 Bill Combiner** - Crop and combine bills into 4-up layout
3. **🔄 Hybrid Bill Generator** - Generate bills with integrated leaflets

### Step-by-Step Usage

#### Leaflet Generator
1. Tap "Leaflet Generator"
2. Tap "Select PDF File"
3. Choose your Meesho order label PDF
4. Tap "Generate Leaflets"
5. Wait for processing to complete
6. Download or share the generated PDF

#### Bill Combiner
1. Tap "Bill Combiner"
2. Select your Meesho bill PDF
3. Tap "Crop and Combine Bills"
4. Download the optimized 4-up layout

#### Hybrid Bill Generator
1. Tap "Hybrid Bill Generator"
2. Select your complete Meesho bill PDF
3. Tap "Generate Hybrid Bills"
4. Get combined bills and leaflets in one PDF

## 📁 File Management

### Where Files Are Stored
- **Input Files**: Temporarily stored during processing
- **Output Files**: Saved in app's internal storage
- **Access Method**: Through the app's download/share functionality

### File Sharing
- **Download**: Opens the PDF in your default PDF viewer
- **Share**: Allows sharing via WhatsApp, email, drive, etc.
- **Location**: Files are automatically managed by the app

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "No file selected" Error
- **Cause**: PDF file wasn't properly selected
- **Solution**: Try selecting the file again, ensure it's a PDF format

#### "No customer names found" Error
- **Cause**: PDF doesn't contain recognizable Meesho order labels
- **Solution**: Verify the PDF contains "BILL TO / SHIP TO" sections

#### App Crashes During Processing
- **Cause**: Large PDF files or insufficient memory
- **Solution**: 
  - Close other apps to free memory
  - Try with smaller PDF files first
  - Restart the app

#### Permission Denied
- **Cause**: Storage permissions not granted
- **Solution**:
  - Go to Settings > Apps > Meesho Helper > Permissions
  - Enable Storage permission
  - Restart the app

#### Can't Open Generated Files
- **Cause**: No PDF viewer app installed
- **Solution**: Install Adobe Acrobat Reader or Google Drive

### Advanced Troubleshooting

#### Clear App Data
If the app is misbehaving:
1. Go to Settings > Apps > Meesho Helper
2. Tap "Storage"
3. Tap "Clear Data" (this will reset the app)
4. Restart the app and grant permissions again

#### Reinstall the App
For persistent issues:
1. Uninstall the current app
2. Download the latest APK version
3. Install fresh and test

## 📊 Performance Tips

### For Best Results
- **PDF Quality**: Use clear, high-quality PDFs
- **File Size**: Smaller files process faster
- **Memory**: Close other apps during processing
- **Storage**: Ensure sufficient free space

### Processing Times
- **Leaflet Generation**: 10-30 seconds depending on customer count
- **Bill Combining**: 15-45 seconds depending on pages
- **Hybrid Bills**: 30-60 seconds for complete processing

## 🔒 Security and Privacy

### Data Security
- All processing happens locally on your device
- No data is sent to external servers
- Files are stored securely in app's private storage

### Permissions Explained
- **Storage Access**: Required to read your PDF files and save outputs
- **File Provider**: Allows sharing generated files with other apps

## 🆕 Updates

### How to Update
1. Download the latest APK when available
2. Install over the existing app (settings will be preserved)
3. Grant any new permissions if requested

### Update Notifications
- Check the repository for new releases
- Updates will include bug fixes and new features

## 📞 Support

### Getting Help
- Check this guide for common solutions
- Verify your device meets minimum requirements
- Test with different PDF files to isolate issues

### Reporting Issues
If you encounter persistent problems:
1. Note the exact error message
2. Record which type of PDF you were processing
3. Include your device model and Android version
4. Report through the appropriate channels

## 🎯 Best Practices

### For Meesho Sellers
1. **Keep Backups**: Always keep original PDF files
2. **Test First**: Try with a small order before processing large batches
3. **Quality Check**: Review generated files before printing
4. **Regular Updates**: Keep the app updated for best performance

### File Organization
- Create folders for different types of orders
- Name files clearly (e.g., "Orders_Jan2024.pdf")
- Regular cleanup of old generated files

---

*This installation guide covers all aspects of setting up and using the Meesho Helper Android app. For additional support, refer to the main README file or contact the development team.*