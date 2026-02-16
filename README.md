<div align="center">

# Asian Player Downloader

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**A modern, feature-rich desktop application for downloading movies and TV series from Asian Player**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Requirements](#-requirements)

</div>

---

## ✨ Features

- 🔍 **Smart Search** - Search through thousands of movies and TV series
- 📺 **Multi-Season Support** - Browse and download episodes by season
- 🎬 **Quality Selection** - Choose from multiple resolutions (360p to 1080p)
- 🌙 **Dark/Light Theme** - Modern UI with theme toggle support
- ⚡ **Batch Downloading** - Download multiple episodes simultaneously
- 📊 **Progress Tracking** - Real-time download progress with speed indicators
- 💾 **Save URLs** - Export download links for later use
- 🎨 **Professional UI** - Clean, modern Arabic interface with responsive design
- 🔄 **Resume Support** - Resume interrupted downloads automatically

---

## 📋 Requirements

### System Requirements

- **Operating System**: Windows 7+, macOS 10.12+, or Linux (Ubuntu 18.04+)
- **Python Version**: Python 3.7 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 100MB for application + space for downloads

### Python Dependencies

All required packages are listed in [`requirements.txt`](requirements.txt):

```
requests>=2.25.0
urllib3>=1.26.0
```

---

## 🚀 Installation

### Step 1: Clone or Download

```bash
# Clone the repository
git clone https://github.com/yourusername/asian-player-downloader.git
cd asian-player-downloader
```

Or download and extract the ZIP file.

### Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
# Start the application
python main.py
```

---

## 📖 Usage

### 1. Authentication

The application automatically authenticates on startup. Wait for the green "✓ مصادق" (Authenticated) indicator before proceeding.

### 2. Search Content

1. Enter a movie or TV series name in Arabic or English
2. Click **🔍 بحث** (Search) or press Enter
3. Browse through the search results

### 3. Select Content

1. Click on a title from the search results
2. For TV series, select the **Season** (الموسم)
3. Choose the **Quality** (الجودة) if desired

### 4. Choose Episodes

1. Click checkboxes next to episodes you want to download
2. Use **✓ تحديد الكل** (Select All) or **✗ إلغاء** (Deselect All) for quick selection
3. Monitor the selected count badge

### 5. Get Download Links

1. Click **📋 الروابط** (Links) to collect URLs
2. View collected links in the log section
3. Click **💾 حفظ** (Save) to export links to a text file

### 6. Download Files

1. Set the **download folder** using the browse button
2. Click **⬇️ تحميل** (Download) to start downloading
3. Monitor progress in the download window
4. Use **✖ إلغاء التحميل** (Cancel) to stop downloads

### 7. Theme Toggle

Click the **🌙** button to switch between light and dark themes.

---

## 🎨 Interface

### Main Window Components

| Section               | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| **Header**            | Search bar, title, theme toggle, and authentication status   |
| **Search Results**    | List of found movies and series with content type indicators |
| **Episode Selection** | Checkboxes for episodes with season and quality selectors    |
| **Downloads & Log**   | Download buttons, folder selection, and activity log         |

### Status Indicators

- 🟡 **جاري المصادقة...** (Authenticating...) - Initial authentication in progress
- 🟢 **✓ مصادق** (Authenticated) - Ready to use
- 🔴 **✗ فشل** (Failed) - Authentication or operation failed

### Keyboard Shortcuts

- **Enter** - Start search when in search field
- **Mouse Wheel** - Scroll through episodes list

---

## 📁 Project Structure

```
asian-player-downloader/
│
├── main.py                 # Main application script
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
└── downloads/             # Default download folder (created automatically)
```

---

## 🔧 Configuration

### Changing Download Location

1. Locate the folder path input in the downloads section
2. Click the **···** button to browse
3. Select your desired folder

### Adjusting Quality Options

Available quality options:

- **الافتراضي** (Default) - Server's default quality
- **360p** - Low quality, smaller file size
- **480p** - Standard quality
- **720p** - HD quality (recommended)
- **1080p** - Full HD quality, larger file size

---

## 🐛 Troubleshooting

### Authentication Fails

- Ensure you have an active internet connection
- Check if the service is temporarily unavailable
- Try restarting the application

### Download Errors

- Verify you have write permissions in the download folder
- Check available disk space
- Ensure the download links are still valid

### Application Won't Start

- Verify Python 3.7+ is installed: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check if tkinter is installed (comes with Python by default)

---

## ⚠️ Disclaimer

This tool is for personal use only. Please respect copyright laws and the terms of service of Asian Player. The authors are not responsible for any misuse of this software.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Support

For support, please open an issue on GitHub or contact the maintainers.

---

## 🙏 Acknowledgments

- Built with [tkinter](https://docs.python.org/3/library/tkinter.html)
- Uses [requests](https://requests.readthedocs.io/) for HTTP requests
- Inspired by the need for better Asian content download tools

---

<div align="center">

**Made with ❤️ for the Asian content community**

[⬆ Back to Top](#asian-player-downloader)

</div>
