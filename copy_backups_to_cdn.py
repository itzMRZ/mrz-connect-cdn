#!/usr/bin/env python3
"""
Copy Normalized Backups to CDN with Proper Dating
Uses estimated semester end dates based on standard BRACU academic calendar
"""

import os
import shutil
from datetime import datetime

# Semester end date estimates (based on typical BRACU academic calendar)
# Format: YYYYMMDD_HHMM
SEMESTER_DATES = {
    "summer-24": "20240831_2359",  # Summer 2024 - End of August
    "fall-24": "20250123_2359",    # Fall 2024 - Late January 2025
    "spring-25": "20250531_2359",  # Spring 2025 - End of May
    "summer-25": "20250831_2359",  # Summer 2025 - End of August
    "fall-25": "20260123_2359",    # Fall 2025 - Late January 2026
}

# Semester naming for the backup files
SEMESTER_NAMES = {
    "summer-24": "Summer2024",
    "fall-24": "Fall2024",
    "spring-25": "Spring2025",
    "summer-25": "Summer2025",
    "fall-25": "Fall2025",
}

def copy_normalized_backups():
    """Copy normalized JSON files to backups directory with proper naming"""
    
    source_dir = "C:/Users/mahar/usis-cdn/normalized_backups"
    dest_dir = "C:/Users/mahar/usis-cdn/backups"
    
    # Create backups directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    print("=" * 70)
    print("Copying Normalized Backups to CDN")
    print("=" * 70)
    
    copied_files = []
    
    # Process each semester
    for semester_key, date_prefix in SEMESTER_DATES.items():
        semester_name = SEMESTER_NAMES[semester_key]
        source_file = os.path.join(source_dir, f"{semester_key}_normalized.json")
        
        # Create backup filename: YYYYMMDD_HHMM_SemesterYYYY_connect.json
        backup_filename = f"{date_prefix}_{semester_name}_connect.json"
        dest_file = os.path.join(dest_dir, backup_filename)
        
        if os.path.exists(source_file):
            # Copy the file
            shutil.copy2(source_file, dest_file)
            
            file_size = os.path.getsize(dest_file) / 1024  # KB
            
            print(f"\n✅ {semester_name}")
            print(f"   Source: {os.path.basename(source_file)}")
            print(f"   Dest:   {backup_filename}")
            print(f"   Size:   {file_size:.1f} KB")
            
            copied_files.append(backup_filename)
        else:
            print(f"\n⚠️  {semester_name}: Source file not found")
    
    print("\n" + "=" * 70)
    print(f"✅ Copied {len(copied_files)} backup files")
    print("=" * 70)
    
    # List all backups in directory
    print("\nAll backups in directory:")
    all_backups = sorted([f for f in os.listdir(dest_dir) if f.endswith('.json')])
    for backup in all_backups:
        file_size = os.path.getsize(os.path.join(dest_dir, backup)) / 1024
        print(f"  - {backup} ({file_size:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("✅ Backup Migration Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the backups in the backups/ directory")
    print("2. Commit and push to GitHub")
    print("3. Backups will be available on your CDN")
    print(f"4. Access via: https://connect-cdn.itzmrz.xyz/backups.html")


if __name__ == "__main__":
    copy_normalized_backups()
