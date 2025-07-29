# 📱 Meesho Helper Android App

A complete Android application that replicates the functionality of the Meesho Helper web tool. This app works offline and provides all the features for processing Meesho orders and generating leaflets directly on your mobile device.

## ✨ Features

### 🏷️ Leaflet Generator
- Upload Meesho order label PDFs from your phone
- Automatically extract customer names from order labels
- Generate personalized thank-you leaflets
- Perfect for including with shipped packages

### 📋 Bill Combiner
- Upload Meesho bill PDFs
- Crop individual bills to remove unnecessary content
- Combine 4 bills per A4 page for efficient printing
- Optimized layout for shipping labels

### 🔄 Hybrid Bill Generator
- Advanced feature combining both functions
- Generates pages with cropped bills AND thank-you leaflets
- Bills positioned at page corners, leaflets in center
- All-in-one solution for order processing

## 📱 Screenshots

*Screenshots will be added after testing the app*

## 🚀 Installation

### Prerequisites
- Android device with API level 24+ (Android 7.0+)
- At least 50MB free storage space
- PDF viewer app (for opening generated files)

### Install from APK
1. Download the APK file from the releases section
2. Enable "Install from unknown sources" in your device settings
3. Open the APK file and follow installation prompts
4. Grant storage permissions when requested

### Install from Source
1. Clone this repository
2. Open the `android-app` folder in Android Studio
3. Build and run the project on your device

## 📖 User Guide

### First Time Setup
1. Open the Meesho Helper app
2. Grant storage permissions when prompted
3. You're ready to start processing PDFs!

### Using Leaflet Generator
1. Tap "Leaflet Generator" on the home screen
2. Tap "Select PDF File" and choose your Meesho order label PDF
3. Tap "Generate Leaflets" and wait for processing
4. Download or share the generated leaflet PDF

### Using Bill Combiner
1. Tap "Bill Combiner" on the home screen
2. Select your Meesho bill PDF
3. Tap "Crop and Combine Bills"
4. Download the 4-up layout PDF for printing

### Using Hybrid Bill Generator
1. Tap "Hybrid Bill Generator" on the home screen
2. Select your Meesho bill PDF
3. Tap "Generate Hybrid Bills"
4. Get a PDF with both bills and personalized leaflets

## 🔧 Technical Details

### Built With
- **Native Android** - Java/Kotlin with Android SDK
- **iText 7** - PDF processing and generation
- **Material Design** - Modern UI components
- **AndroidX** - Latest Android support libraries

### Architecture
- **MVVM Pattern** - Clean separation of concerns
- **Async Processing** - Background PDF operations
- **File Management** - Secure local storage
- **Permission Handling** - Runtime permission requests

### Key Components
- `MainActivity` - Main navigation hub
- `LeafletGeneratorActivity` - Leaflet generation functionality
- `BillCombinerActivity` - Bill cropping and combining
- `HybridBillActivity` - Hybrid bill generation
- `PDFProcessor` - Core PDF manipulation utilities
- `LeafletGenerator` - Thank-you leaflet creation
- `FileManager` - File operations and storage

## 🛠️ Development

### Building the Project
```bash
cd android-app
./gradlew assembleDebug
```

### Running Tests
```bash
./gradlew test
```

### Creating Release APK
```bash
./gradlew assembleRelease
```

### Project Structure
```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/meeshohelper/
│   │   │   ├── MainActivity.java
│   │   │   ├── activities/
│   │   │   ├── utils/
│   │   │   └── models/
│   │   ├── res/
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── gradle/
├── build.gradle
└── settings.gradle
```

## 🔒 Permissions

The app requires the following permissions:
- **Storage Access** - To read PDF files and save generated outputs
- **File Provider** - To share generated PDFs with other apps

## 📁 File Management

### Storage Locations
- **Temp Files**: `Android/data/com.meeshohelper/files/MeeshoHelper/temp/`
- **Output Files**: `Android/data/com.meeshohelper/files/MeeshoHelper/output/`

### File Cleanup
- Temporary files are automatically cleaned up
- Output files are kept until manually deleted
- App data can be cleared through device settings

## 🐛 Troubleshooting

### Common Issues

**App crashes on PDF processing**
- Ensure the PDF file is not corrupted
- Check available storage space
- Try with a smaller PDF file first

**No customer names found**
- Verify the PDF contains Meesho order labels
- Check if the PDF has the "BILL TO / SHIP TO" format
- Some PDFs may have different text encoding

**Can't share generated files**
- Ensure you have a PDF viewer app installed
- Check if the sharing app supports PDF files
- Try opening the file directly first

**Permission denied errors**
- Go to Settings > Apps > Meesho Helper > Permissions
- Enable Storage permission
- Restart the app after enabling permissions

### Getting Help
If you encounter issues:
1. Check the troubleshooting section above
2. Ensure your device meets the minimum requirements
3. Try restarting the app
4. Clear app data if problems persist

## 🔄 Updates

The app will be updated periodically with:
- Bug fixes and performance improvements
- New PDF processing capabilities
- Enhanced user interface
- Additional customization options

## 📄 License

This project is for personal and commercial use by Meesho sellers. Please respect the intellectual property and licensing terms.

## 👨‍💻 Developer

Developed as an Android companion to the Meesho Helper web application, providing the same powerful PDF processing capabilities in a mobile-friendly format.

---

*For any issues or suggestions, please contact the development team.*