# 🎓 Unified Exam Security Systems

A unified platform combining two exam monitoring systems:

## 🌟 Systems Overview

### 💻 Online Exam System
- **Project**: Güvenli Sınav Denetim Sistemi  
- **Port**: http://localhost:5000
- **Tech Stack**: Flask + OpenCV + YOLO
- **Use Case**: Remote online exam monitoring

**Features:**
- ✅ Real-time camera monitoring
- ✅ Face, eye, mouth detection
- ✅ Object detection (phone, book)
- ✅ Automatic violation recording
- ✅ Live dashboard
- ✅ Detailed reporting

### 🏫 Classroom Exam System
- **Project**: EduView
- **Port**: http://localhost:3000
- **Tech Stack**: Reflex + AI Models
- **Use Case**: In-class physical exam monitoring

**Features:**
- ✅ 3 AI Detection Models
- ✅ Advanced eye tracking
- ✅ Behavior analysis
- ✅ Classroom activity detection
- ✅ Cheating behavior detection
- ✅ Configurable thresholds

---

## 🚀 Quick Start

### Easiest Method (Recommended):

**Double-click:** `LAUNCH_SYSTEMS.bat`

Browser will automatically open at: `http://localhost:8080`

### From Command Line:

```bash
python unified_launcher.py
```

### Manual Access:

Open your browser and go to: `http://localhost:8080`

---

## 📋 Prerequisites

### For Online System (Already Included):
```bash
cd "Güvenli Sınav Denetim Sistemi"
pip install -r requirements.txt
```

### For Classroom System (First Time Setup):
```bash
cd ..
git clone https://github.com/Laoode/EduView.git EduView_main
cd EduView_main
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 🗂️ Required Folder Structure

```
Downloads/
├── Güvenli Sınav Denetim Sistemi/    ← This folder
│   ├── unified_launcher.py           ← Unified server
│   ├── launcher_index.html           ← Selection page
│   ├── LAUNCH_SYSTEMS.bat            ← Launch script
│   ├── start_system.py               ← Online system
│   └── ...
│
└── EduView_main/                      ← EduView folder (must install)
    ├── object_cheating/
    ├── requirements.txt
    ├── rxconfig.py
    └── ...
```

---

## 🎯 How It Works

### Architecture

```
Launcher (Port 8080)
├── Selection Page
│   ├── [1] Online System → Starts Flask (Port 5000)
│   └── [2] Classroom System → Starts Reflex (Port 3000)
```

### Workflow

1. **Start Launcher**: Run `LAUNCH_SYSTEMS.bat`
2. **Choose System**: Click on desired system card
3. **Auto Launch**: System starts automatically
4. **Auto Redirect**: Browser redirects to system

---

## ⚙️ Configuration

### Ports
- **Launcher**: 8080
- **Online System**: 5000
- **Classroom System**: 3000

### Keyboard Shortcuts
From selection page:
- Press `1` → Launch Online System
- Press `2` → Launch Classroom System

---

## 🔍 Troubleshooting

### Port 8080 Already in Use
```bash
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### EduView Not Found
```bash
cd ..
git clone https://github.com/Laoode/EduView.git EduView_main
cd EduView_main
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### System Doesn't Auto-Open
- Manually open browser
- Navigate to `http://localhost:8080`

---

## 📊 System Comparison

| Feature | Online | Classroom |
|---------|--------|-----------|
| Port | 5000 | 3000 |
| Framework | Flask | Reflex |
| Detection | Face/Eye/Mouth/Object | 3 AI Models |
| Reports | JSON + HTML | Interactive Dashboard |
| Usage | Remote | In-Class |
| Eye Tracking | Basic | Advanced |
| Behavior Analysis | Real-time | AI-Scored |

---

## 📚 Documentation

- **Online System**: See `Proje_Dokumantasyon.txt`
- **Classroom System**: https://github.com/Laoode/EduView
- **Unified Guide (Arabic)**: See `UNIFIED_GUIDE.md`

---

## 🎨 Features

### Beautiful Selection Interface
- Modern gradient design
- Interactive cards with hover effects
- Smooth animations
- Responsive layout
- Keyboard navigation

### Automatic System Management
- Launch systems on demand
- Track system status
- Auto-redirect to system
- Process management

### Multi-Language Support
- Turkish interface
- English documentation
- Arabic guide

---

## 💡 Usage Tips

### First Time Setup:
1. Run `LAUNCH_SYSTEMS.bat`
2. If choosing Classroom System and error appears:
   - Follow on-screen instructions
   - Install EduView manually
   - Return to launcher and try again

### Regular Use:
1. Run `LAUNCH_SYSTEMS.bat`
2. Choose desired system
3. System launches automatically
4. Start monitoring!

---

## 🛠️ Technical Details

### Unified Launcher (`unified_launcher.py`)
- Flask-based web server
- Process management for both systems
- REST API for system control
- Auto browser opening

### Selection Page (`launcher_index.html`)
- Pure HTML/CSS/JS
- No dependencies
- Responsive design
- Accessible UI

---

## 📦 Files Created

1. **`unified_launcher.py`** - Main launcher server
2. **`launcher_index.html`** - Selection interface
3. **`LAUNCH_SYSTEMS.bat`** - Windows launcher script
4. **`UNIFIED_GUIDE.md`** - Arabic documentation
5. **`UNIFIED_README.md`** - This file

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

- **Online System Issues**: Open issue in this repository
- **Classroom System (EduView)**: https://github.com/Laoode/EduView/issues

---

## ✨ Quick Summary

**Simple Launch:**
```
LAUNCH_SYSTEMS.bat → Choose System → Use!
```

**Access Points:**
- Launcher: http://localhost:8080
- Online: http://localhost:5000
- Classroom: http://localhost:3000

**🎉 Enjoy the Unified Exam Security Platform!**
