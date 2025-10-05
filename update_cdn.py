#!/usr/bin/env python3
"""
MRZ Connect CDN Data Update Script
Fetches course data from MRZ Connect API and generates static CDN files with metadata.
"""

import json
import os
import gzip
import requests
import shutil
import glob
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")


def fetch_mrz_data() -> List[Dict]:
    """Fetch course data from MRZ Connect API."""
    url = "https://usis-cdn.eniamza.com/connect.json"
    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Successfully fetched {len(data)} sections")
        return data
    except requests.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        raise


def calculate_connect_metadata(sections: List[Dict]) -> Dict:
    """Calculate metadata for connect.json."""
    print("Calculating connect.json metadata...")
    
    # Initialize values
    section_ids = []
    total_consumed = 0
    total_capacity = 0
    mid_dates = []
    final_dates = []
    
    # Process each section
    for section in sections:
        section_ids.append(section['sectionId'])
        total_consumed += section.get('consumedSeat', 0)
        total_capacity += section.get('capacity', 0)
        
        # Extract exam dates
        schedule = section.get('sectionSchedule', {})
        if schedule:
            mid_date = schedule.get('midExamDate')
            final_date = schedule.get('finalExamDate')
            
            if mid_date:
                mid_dates.append(mid_date)
            if final_date:
                final_dates.append(final_date)
    
    # Sort dates
    mid_dates.sort()
    final_dates.sort()
    
    metadata = {
        "firstSectionId": min(section_ids) if section_ids else None,
        "lastSectionId": max(section_ids) if section_ids else None,
        "totalSections": len(sections),
        "totalConsumedSeats": total_consumed,
        "totalEmptySeats": total_capacity - total_consumed,
        "totalCapacity": total_capacity,
        "midExamStartDate": mid_dates[0] if mid_dates else None,
        "midExamEndDate": mid_dates[-1] if mid_dates else None,
        "finalExamStartDate": final_dates[0] if final_dates else None,
        "finalExamEndDate": final_dates[-1] if final_dates else None,
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"✓ Metadata calculated:")
    print(f"  - Total sections: {metadata['totalSections']}")
    print(f"  - Total consumed seats: {metadata['totalConsumedSeats']}")
    print(f"  - Total empty seats: {metadata['totalEmptySeats']}")
    print(f"  - Mid exams: {metadata['midExamStartDate']} to {metadata['midExamEndDate']}")
    print(f"  - Final exams: {metadata['finalExamStartDate']} to {metadata['finalExamEndDate']}")
    
    return metadata


def generate_connect_json(sections: List[Dict], output_path: str = "connect.json"):
    """Generate connect.json with metadata."""
    # Ensure output path is in the script directory
    if not os.path.isabs(output_path):
        output_path = os.path.join(SCRIPT_DIR, output_path)
    
    print(f"\nGenerating {output_path}...")
    
    metadata = calculate_connect_metadata(sections)
    
    output_data = {
        "metadata": metadata,
        "sections": sections
    }
    
    # Write regular JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Write gzipped version
    gzip_path = output_path + '.gz'
    with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
        json.dump(output_data, f, separators=(',', ':'), ensure_ascii=False)
    
    regular_size = os.path.getsize(output_path) / 1024  # KB
    gzip_size = os.path.getsize(gzip_path) / 1024  # KB
    compression_ratio = ((regular_size - gzip_size) / regular_size * 100)
    
    print(f"✓ {output_path} created successfully")
    print(f"  Regular: {regular_size:.1f} KB")
    print(f"  Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")


def get_current_semester(mid_exam_start: str) -> str:
    """Determine current semester based on mid exam start date."""
    if not mid_exam_start:
        return "Unknown"
    
    try:
        date = datetime.strptime(mid_exam_start, "%Y-%m-%d")
        month = date.month
        year = date.year
        
        # Determine semester
        if 1 <= month <= 4:
            return f"Spring{year}"
        elif 5 <= month <= 8:
            return f"Summer{year}"
        else:  # 9-12
            return f"Fall{year}"
    except:
        return "Unknown"


def manage_current_backup(metadata: Dict, sections: List[Dict]):
    """Manage current semester backup with smart renaming."""
    print("\n" + "=" * 60)
    print("Managing Current Semester Backup")
    print("=" * 60)
    
    # Ensure backups directory exists
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    
    # Get current semester info
    mid_exam_start = metadata.get('midExamStartDate')
    current_semester = get_current_semester(mid_exam_start)
    semester_changed = False
    
    print(f"\nCurrent Semester: {current_semester}")
    print(f"Mid Exam Start: {mid_exam_start}")
    
    # Look for existing "curr_" backup
    curr_backups = glob.glob(os.path.join(BACKUPS_DIR, "curr_*_connect.json"))
    
    if curr_backups:
        old_curr_backup = curr_backups[0]
        print(f"\nFound existing current backup: {os.path.basename(old_curr_backup)}")
        
        # Load old backup to check if exam dates changed
        try:
            with open(old_curr_backup, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                old_mid_exam = old_data['metadata'].get('midExamStartDate')
                old_semester = get_current_semester(old_mid_exam)
            
            # Check if semester changed (exam dates different)
            if mid_exam_start != old_mid_exam:
                semester_changed = True
                print(f"\n📅 Exam dates changed!")
                print(f"   Old: {old_mid_exam} ({old_semester})")
                print(f"   New: {mid_exam_start} ({current_semester})")
                
                # Rename old backup with final exam date
                old_final_exam = old_data['metadata'].get('finalExamEndDate')
                if old_final_exam:
                    final_date_obj = datetime.strptime(old_final_exam, "%Y-%m-%d")
                    date_prefix = final_date_obj.strftime("%Y%m%d_2359")
                    new_backup_name = f"{date_prefix}_{old_semester}_connect.json"
                    new_backup_path = os.path.join(BACKUPS_DIR, new_backup_name)
                    
                    # Rename the old current backup
                    shutil.move(old_curr_backup, new_backup_path)
                    print(f"✓ Archived old backup as: {new_backup_name}")
                else:
                    print(f"⚠️  No final exam date in old backup, removing...")
                    os.remove(old_curr_backup)
            else:
                print(f"✓ Same semester, updating current backup...")
        except Exception as e:
            print(f"⚠️  Error reading old backup: {e}")
    else:
        # No previous backup found, this is a new semester
        semester_changed = True
    
    # Create new current backup
    curr_backup_name = f"curr_{current_semester}_connect.json"
    curr_backup_path = os.path.join(BACKUPS_DIR, curr_backup_name)
    
    backup_data = {
        "metadata": metadata,
        "sections": sections
    }
    
    with open(curr_backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(curr_backup_path) / 1024
    print(f"\n✓ Created/Updated: {curr_backup_name} ({file_size:.1f} KB)")
    print(f"  This will be renamed when semester ends")
    
    return curr_backup_name, semester_changed


def generate_exams_json(sections: List[Dict], output_path: str = "exams.json"):
    """Generate exams.json with exam schedule data."""
    # Ensure output path is in the script directory
    if not os.path.isabs(output_path):
        output_path = os.path.join(SCRIPT_DIR, output_path)
    
    print(f"\nGenerating {output_path}...")
    
    exams = []
    mid_dates = []
    final_dates = []
    
    for section in sections:
        schedule = section.get('sectionSchedule', {})
        if not schedule:
            continue
        
        mid_date = schedule.get('midExamDate')
        mid_time = schedule.get('midExamStartTime')
        final_date = schedule.get('finalExamDate')
        final_time = schedule.get('finalExamStartTime')
        
        # Skip sections without exam dates (typically LAB sections)
        if not mid_date and not final_date:
            continue
        
        exam_entry = {
            "courseCode": section.get('courseCode'),
            "sectionName": section.get('sectionName'),
            "sectionId": section.get('sectionId'),
            "sectionType": section.get('sectionType'),
            "midExamDate": mid_date,
            "midExamTime": mid_time,
            "midExamRoom": None,  # To be updated later
            "finalExamDate": final_date,
            "finalExamTime": final_time,
            "finalExamRoom": None  # To be updated later
        }
        
        exams.append(exam_entry)
        
        # Collect dates for metadata
        if mid_date:
            mid_dates.append(mid_date)
        if final_date:
            final_dates.append(final_date)
    
    # Sort dates
    mid_dates.sort()
    final_dates.sort()
    
    metadata = {
        "totalExams": len(exams),
        "midExamStartDate": mid_dates[0] if mid_dates else None,
        "midExamEndDate": mid_dates[-1] if mid_dates else None,
        "finalExamStartDate": final_dates[0] if final_dates else None,
        "finalExamEndDate": final_dates[-1] if final_dates else None,
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }
    
    output_data = {
        "metadata": metadata,
        "exams": exams
    }
    
    # Write regular JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Write gzipped version
    gzip_path = output_path + '.gz'
    with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
        json.dump(output_data, f, separators=(',', ':'), ensure_ascii=False)
    
    regular_size = os.path.getsize(output_path) / 1024  # KB
    gzip_size = os.path.getsize(gzip_path) / 1024  # KB
    compression_ratio = ((regular_size - gzip_size) / regular_size * 100)
    
    print(f"✓ {output_path} created successfully")
    print(f"  Regular: {regular_size:.1f} KB | Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")
    print(f"  Total exams: {metadata['totalExams']}")
    print(f"  Mid exams: {metadata['midExamStartDate']} to {metadata['midExamEndDate']}")
    print(f"  Final exams: {metadata['finalExamStartDate']} to {metadata['finalExamEndDate']}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("MRZ Connect CDN Data Update Script")
    print("=" * 60)
    
    try:
        # Fetch data from API
        sections = fetch_mrz_data()
        
        # Calculate metadata first (needed for backup management)
        metadata = calculate_connect_metadata(sections)
        
        # Manage current semester backup
        curr_backup_name, semester_changed = manage_current_backup(metadata, sections)
        
        # Generate both JSON files
        output_data = {
            "metadata": metadata,
            "sections": sections
        }
        
        # Write connect.json
        connect_path = os.path.join(SCRIPT_DIR, "connect.json")
        with open(connect_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Write gzipped version
        gzip_path = connect_path + '.gz'
        with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
            json.dump(output_data, f, separators=(',', ':'), ensure_ascii=False)
        
        regular_size = os.path.getsize(connect_path) / 1024
        gzip_size = os.path.getsize(gzip_path) / 1024
        compression_ratio = ((regular_size - gzip_size) / regular_size * 100)
        
        print(f"\n✓ connect.json created successfully")
        print(f"  Regular: {regular_size:.1f} KB")
        print(f"  Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")
        
        # Generate exams.json
        generate_exams_json(sections)
        
        # Generate backup index
        print("\n" + "=" * 60)
        print("Generating Backup Index")
        print("=" * 60)
        
        from generate_backup_index import generate_backup_index
        generate_backup_index()
        
        # Generate free labs CDN if semester changed
        if semester_changed:
            print("\n" + "=" * 60)
            print("🆕 Semester changed - Generating Free Labs CDN")
            print("=" * 60)
            try:
                from generate_free_labs import generate_free_labs_json
                generate_free_labs_json()
            except Exception as e:
                print(f"⚠️  Error generating free labs: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n⏭️  Same semester - Skipping free labs generation")
        
        print("\n" + "=" * 60)
        print("✓ All files generated successfully!")
        print("=" * 60)
        print(f"\nCurrent semester backup: {curr_backup_name}")
        print("Backup index: connect_backup.json")
        if semester_changed:
            print("Free labs CDN: free_labs.json")
        print("\nNext steps:")
        print("1. Review the generated JSON files")
        print("2. Commit and push to GitHub")
        print("3. Backups will auto-archive when semester ends")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
