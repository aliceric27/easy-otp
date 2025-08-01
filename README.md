# Easy OTP

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-TW.md">繁體中文</a>
</p>

A modern and elegant OTP (One-Time Password) manager with a user-friendly interface and powerful features.

![demo](demo.png)

## ✨ Features

- 🔐 **Secure Local Storage** - All data stored locally, no internet required
- 📷 **QR Code Support** - Quick import via QR code scanning
- 🎨 **Modern UI** - Dark theme, rounded corners, smooth animations
- ⏱️ **Visual Countdown** - Circular progress bar showing remaining time
- 📤 **Multi-format Export** - Supports JSON, QR Code, CSV formats
- 🔍 **Real-time Search** - Quickly find the OTP you need
- 📋 **One-click Copy** - Click to copy OTP code
- 🌐 **Multi-language** - Supports English and Traditional Chinese

## 🚀 Quick Start

### Method 1: Direct Execution (Recommended)

1. Download the latest `EasyOTP.exe`
2. Double-click to run

### Method 2: Run from Source

1. Install Python 3.8 or higher
2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/easy-otp.git
   cd easy-otp
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python easy_otp.py
   ```

## 📦 Building Executable

To build your own executable:

```bash
python build.py
```

The executable will be in the `dist/` directory.

## 🛠️ Tech Stack

- **GUI Framework**: CustomTkinter + Tkinter
- **OTP Processing**: PyOTP
- **QR Code**: pyzbar + qrcode
- **Packaging**: PyInstaller

## 📂 Project Structure

```
easy-otp/
├── src/
│   ├── ui/                  # UI related
│   │   ├── main_window.py   # Main window
│   │   ├── components/      # UI components
│   │   └── themes/          # Theme settings
│   ├── core/                # Core functionality
│   │   ├── otp_manager.py   # OTP management
│   │   ├── storage.py       # Data storage
│   │   └── settings.py      # Settings management
│   ├── utils/               # Utility functions
│   │   ├── qr_handler.py    # QR code handling
│   │   ├── export_import.py # Export/import
│   │   └── i18n.py          # Internationalization
│   └── assets/              # Resources
│       └── locales/         # Translation files
├── requirements.txt         # Dependencies
├── build.py                # Build script
├── easy_otp.py             # Entry point
└── README.md               # Documentation
```

## 💡 Usage Guide

### Adding OTP

1. **Scan QR Code**: Click "Add" → "Upload QR Code", select image with OTP QR code
2. **Manual Input**: Click "Add" → "Manual Input", enter label and secret key
3. **Batch Import**: Click "Add" → "Batch Import", import from JSON or QR code directory

### Using OTP

- Click OTP code to copy to clipboard
- Circular progress bar shows remaining validity time
- Use search box to quickly find OTP

### Export & Backup

1. Click "..." button in top-right corner
2. Choose export format:
   - **JSON**: Complete data for backup
   - **QR Code**: Generate QR code image for each OTP
   - **CSV**: Spreadsheet format for viewing

## ⚠️ Notes

- Windows users may need to install [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
- First run may trigger antivirus warnings, please add to trusted list
- Keep exported files secure to prevent leaks

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is licensed under the MIT License.