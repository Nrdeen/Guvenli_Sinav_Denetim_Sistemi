# Exam Proctoring System - Updated Version
# نظام مراقبة الامتحانات - النسخة المحدثة

## 🆕 New Features - الميزات الجديدة

### 3 Monitoring Modes - 3 أوضاع للمراقبة

1. **🏫 Classroom Monitoring - مراقبة الصف**
   - Multiple RTSP cameras support
   - Real-time face recognition
   - Object detection (phones, books, laptops)
   - Multi-student detection

2. **💻 Online Monitoring - مراقبة أونلاين**
   - Individual student webcam monitoring
   - Face recognition verification
   - Eye tracking
   - Prohibited object detection

3. **🔄 Combined Mode - الوضع المشترك**
   - Both classroom + online simultaneously
   - Parallel monitoring threads

### Face Recognition - التعرف على الوجه

- Automatic student identification by face
- Each student has a photo in the system
- Real-time matching during exam
- Confidence scores displayed

## 📁 New Project Structure

```
exam-proctoring/
│
├── config/
│   ├── students.yaml        ← Student profiles with photos
│   ├── cameras.yaml         ← Classroom camera configuration
│   └── config.yaml
│
├── students_photos/         ← Student face photos
│   ├── s01.jpg
│   ├── s02.jpg
│   └── s03.jpg
│
├── src/
│   ├── main_menu.py         ← Main menu with 3 options
│   │
│   ├── classroom_monitor/   ← Classroom monitoring
│   │   ├── __init__.py
│   │   └── rtsp_reader.py
│   │
│   ├── online_agent/        ← Online student monitoring
│   │   ├── __init__.py
│   │   └── agent.py
│   │
│   ├── combined/            ← Combined mode
│   │   ├── __init__.py
│   │   └── run_both.py
│   │
│   ├── detection/
│   │   ├── face_id.py       ← Face recognition (NEW)
│   │   └── ...
│   │
│   └── utils/
│       ├── student_loader.py ← Load student data (NEW)
│       └── ...
│
└── run.py                   ← Main entry point
```

## 🚀 Quick Start - البدء السريع

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important**: Make sure to install `face-recognition` and `dlib`:

```bash
pip install face-recognition dlib
```

### 2. Add Student Photos

1. Add student face photos to `students_photos/` folder
2. Name them: `s01.jpg`, `s02.jpg`, `s03.jpg`, etc.
3. Use clear, front-facing photos with good lighting

### 3. Configure Students

Edit `config/students.yaml`:

```yaml
students:
  - id: s01
    name: "Ali Mohammed"
    photo: "students_photos/s01.jpg"
  
  - id: s02
    name: "Sara Kamal"
    photo: "students_photos/s02.jpg"
```

### 4. Configure Cameras (for Classroom Mode)

Edit `config/cameras.yaml`:

```yaml
cameras:
  - id: cam01
    name: "Front Camera"
    rtsp: "rtsp://192.168.1.20/live"
  
  - id: cam02
    name: "Back Camera"
    rtsp: "rtsp://192.168.1.21/stream"
```

**For Testing**: You can use webcam index (0, 1, 2) instead of RTSP URLs.

### 5. Run the System

```bash
python run.py
```

## 📖 How to Use - كيفية الاستخدام

### Starting the System

1. Run `python run.py`
2. You'll see 3 options:
   - Option 1: Classroom Monitoring
   - Option 2: Online Monitoring
   - Option 3: Combined Mode

### Option 1: Classroom Monitoring

- Monitors multiple classroom cameras
- Automatically recognizes students
- Detects violations (multiple faces, prohibited objects)
- Press 'q' to stop

### Option 2: Online Monitoring

- For remote/online exams
- Each student selects their profile
- Monitors via webcam
- Tracks eye movement, face presence, talking
- Press 'q' to stop

### Option 3: Combined Mode

- Runs both modes simultaneously
- For hybrid exams (some students in classroom, some online)
- Press Ctrl+C to stop

## 🎯 Face Recognition Features

### Automatic Student Identification

- System loads all student photos on startup
- Creates face encodings for each student
- Matches faces in real-time during monitoring
- Shows student name and ID on screen

### Confidence Scores

- Each face match has a confidence percentage
- Green box = Recognized student
- Red box = Unknown person

### Violation Detection

- Wrong student detected
- Student left camera view
- Multiple people in frame
- Prohibited objects detected

## ⚙️ Settings Menu

Access via Option 4 in main menu:

1. **View Students List** - See all registered students
2. **View Camera Configuration** - See camera setup
3. **Test Face Recognition** - Test with webcam
4. **System Information** - View system details

## 📝 Configuration Files

### students.yaml

```yaml
students:
  - id: s01              # Unique student ID
    name: "Student Name" # Full name
    photo: "path/to/photo.jpg"  # Photo path
```

### cameras.yaml

```yaml
cameras:
  - id: cam01           # Unique camera ID
    name: "Camera Name" # Descriptive name
    rtsp: "rtsp://..."  # RTSP URL or webcam index
```

## 🔧 Troubleshooting

### Face Recognition Not Working

1. Check if `face-recognition` is installed:
   ```bash
   pip install face-recognition
   ```

2. Ensure photos are in correct format (JPG/PNG)

3. Photos should have:
   - Clear face visibility
   - Good lighting
   - One face per photo
   - Front-facing

### Camera Not Opening

1. For RTSP cameras:
   - Verify RTSP URL is correct
   - Check network connection
   - Test with VLC player first

2. For webcams:
   - Check camera permissions
   - Try different index (0, 1, 2)
   - Ensure no other app is using camera

### Performance Issues

1. Reduce frame processing frequency
2. Use lower resolution cameras
3. Close other applications
4. Check CPU/GPU usage

## 📊 Violation Logs

All violations are logged in:
- `reports/violations.json` - JSON log
- `reports/violation_captures/` - Screenshots

## 🔒 Security & Privacy

- Student photos are stored locally
- No data sent to external servers
- Access controlled via system permissions
- Logs stored securely

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review configuration files
3. Test individual components
4. Check system logs

## 🎓 Best Practices

### Before Exam

1. ✅ Add all student photos
2. ✅ Test camera connections
3. ✅ Verify face recognition accuracy
4. ✅ Check network stability
5. ✅ Test full monitoring session

### During Exam

1. ✅ Monitor violation logs
2. ✅ Watch for system alerts
3. ✅ Check camera feeds regularly
4. ✅ Note any technical issues

### After Exam

1. ✅ Review violation reports
2. ✅ Save recordings
3. ✅ Generate PDF reports
4. ✅ Archive exam data

## 📈 System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Camera**: 720p or higher
- **Network**: Stable connection for RTSP cameras

## 🆕 Updates

### Version 2.0 (Current)

- ✅ Face recognition system
- ✅ Student photo database
- ✅ Three monitoring modes
- ✅ Improved UI with menu
- ✅ Settings configuration
- ✅ Real-time student identification

### Version 1.0

- Basic monitoring
- Single mode operation
- Manual student entry

---

Made with ❤️ for secure exam proctoring
صُنع بحب من أجل مراقبة آمنة للامتحانات
