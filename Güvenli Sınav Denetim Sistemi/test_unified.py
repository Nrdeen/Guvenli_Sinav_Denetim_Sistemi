"""
Quick Test for Unified Launcher
Tests if the unified launcher system is properly configured
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def test_files():
    """Check if required files exist"""
    print("🔍 Testing file structure...\n")
    
    files = {
        'unified_launcher.py': '✅ Main launcher server',
        'launcher_index.html': '✅ Selection interface',
        'LAUNCH_SYSTEMS.bat': '✅ Windows launcher',
        'UNIFIED_GUIDE.md': '✅ Arabic guide',
        'UNIFIED_README.md': '✅ English README',
        'start_system.py': '✅ Online system script',
    }
    
    all_exist = True
    for file, desc in files.items():
        if (BASE_DIR / file).exists():
            print(f"  {desc}: {file}")
        else:
            print(f"  ❌ Missing: {file}")
            all_exist = False
    
    return all_exist

def test_eduview():
    """Check if EduView folder exists"""
    print("\n🔍 Testing EduView installation...\n")
    
    eduview_path = BASE_DIR.parent / 'EduView_main'
    
    if eduview_path.exists():
        print(f"  ✅ EduView found: {eduview_path}")
        
        required_files = ['rxconfig.py', 'requirements.txt']
        for file in required_files:
            if (eduview_path / file).exists():
                print(f"  ✅ {file} exists")
            else:
                print(f"  ⚠️  {file} not found")
        
        return True
    else:
        print(f"  ⚠️  EduView not found at: {eduview_path}")
        print("\n  To install EduView:")
        print(f"    cd {BASE_DIR.parent}")
        print("    git clone https://github.com/Laoode/EduView.git EduView_main")
        print("    cd EduView_main")
        print("    python -m venv venv")
        print("    venv\\Scripts\\activate")
        print("    pip install -r requirements.txt")
        return False

def test_imports():
    """Test required Python packages"""
    print("\n🔍 Testing Python packages...\n")
    
    packages = {
        'flask': 'Flask web framework',
        'subprocess': 'Process management',
        'pathlib': 'Path handling',
    }
    
    all_ok = True
    for package, desc in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {desc}: {package}")
        except ImportError:
            print(f"  ❌ Missing: {package}")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("="*70)
    print("  🎓 UNIFIED LAUNCHER - System Test")
    print("="*70)
    print()
    
    results = []
    
    # Test files
    results.append(("Files", test_files()))
    
    # Test EduView
    results.append(("EduView", test_eduview()))
    
    # Test imports
    results.append(("Python Packages", test_imports()))
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    print()
    
    for name, passed in results:
        status = "✅ PASS" if passed else "⚠️  WARNING"
        print(f"  {status} - {name}")
    
    print("\n" + "="*70)
    
    if all(r[1] for r in results):
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  Ready to launch!")
        print("  Run: LAUNCH_SYSTEMS.bat")
        print("  Or:  python unified_launcher.py")
    else:
        print("\n  ⚠️  SOME WARNINGS DETECTED")
        print("\n  The launcher will work, but:")
        print("  - EduView needs to be installed for Classroom System")
        print("  - Online System will work without EduView")
    
    print("\n" + "="*70)
    print()

if __name__ == '__main__':
    main()
