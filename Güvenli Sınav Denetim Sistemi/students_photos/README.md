# Students Photos Directory

This folder contains student face photos for the face recognition system.

## Instructions:

1. **Add student photos** with the naming format: `s01.jpg`, `s02.jpg`, `s03.jpg`, etc.
   - Match the IDs in `config/students.yaml`

2. **Photo Requirements:**
   - Clear front-facing photo of the student
   - Good lighting
   - Neutral background
   - Only one face in the photo
   - Recommended size: 640x480 or higher
   - Format: JPG or PNG

3. **Example:**
   ```
   students_photos/
   ├── s01.jpg  (Ali Mohammed)
   ├── s02.jpg  (Sara Kamal)
   └── s03.jpg  (Yusuf Demir)
   ```

4. **Testing:**
   - After adding photos, run the system to verify face recognition works properly
   - The system will automatically load and encode faces on startup

## Note:
- Keep this folder secure and private
- Only authorized personnel should have access
- Photos are used only for exam proctoring purposes
