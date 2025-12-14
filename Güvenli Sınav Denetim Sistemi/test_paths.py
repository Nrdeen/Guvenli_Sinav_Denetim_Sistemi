from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print(f"BASE_DIR: {BASE_DIR}")
print(f"BASE_DIR.parent: {BASE_DIR.parent}")

eduview_path = BASE_DIR.parent / 'EduView-main'
print(f"\nEduView path: {eduview_path}")
print(f"Exists: {eduview_path.exists()}")
print(f"rxconfig.py exists: {(eduview_path / 'rxconfig.py').exists()}")

print("\nAll EduView folders in parent:")
for item in BASE_DIR.parent.iterdir():
    if 'eduview' in item.name.lower():
        print(f"  - {item.name} (is_dir: {item.is_dir()})")
