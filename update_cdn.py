#!/usr/bin/env python3
"""
MRZ Connect CDN Data Update Script
Fetches course data from MRZ Connect API and generates static CDN files with metadata.
"""

import json
import os
import sys
import gzip
import requests
import glob
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")
VERSION_FILE = os.path.join(SCRIPT_DIR, "version.json")


def load_version() -> Dict:
    """Load version info from version.json."""
    try:
        with open(VERSION_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"major": 2, "semester": 0, "daily": 0}


def bump_version(semester_changed: bool) -> str:
    """Bump version and return version string (MAJOR.SEMESTER.DAILY)."""
    v = load_version()

    if semester_changed:
        v["semester"] += 1
        v["daily"] = 0
    else:
        v["daily"] += 1

    with open(VERSION_FILE, 'w') as f:
        json.dump(v, f, indent=2)

    version_str = f"{v['major']}.{v['semester']}.{v['daily']}"
    print(f"✓ Version bumped to {version_str}")
    return version_str


def fetch_mrz_data(force: bool = False) -> Optional[List[Dict]]:
    """Fetch course data from MRZ Connect API with conditional GET."""
    url = "https://usis-cdn.eniamza.com/connect.json"
    etag_file = os.path.join(SCRIPT_DIR, "connect.etag")
    headers = {}

    # Load stored ETag (skip if force mode)
    if not force and os.path.exists(etag_file):
        with open(etag_file, 'r') as f:
            stored_etag = f.read().strip()
            if stored_etag:
                headers['If-None-Match'] = stored_etag

    print(f"Fetching data from {url}...")
    if force:
        print("  (force mode - ignoring cached ETag)")

    try:
        response = requests.get(url, headers=headers, timeout=30)

        # Check for 304 Not Modified
        if response.status_code == 304:
            print("✓ Data not modified (304). Skipping update.")
            return None

        response.raise_for_status()

        # Save new ETag
        if 'ETag' in response.headers:
            with open(etag_file, 'w') as f:
                f.write(response.headers['ETag'])

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
    print(
        f"  - Mid exams: {metadata['midExamStartDate']} to {metadata['midExamEndDate']}")
    print(
        f"  - Final exams: {metadata['finalExamStartDate']} to {metadata['finalExamEndDate']}")

    return metadata


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


def semester_to_filename(semester: str) -> str:
    """Convert semester name to clean filename: Spring2026 → spring2026.json"""
    return semester.lower() + ".json"


def manage_current_backup(metadata: Dict, sections: List[Dict]):
    """Manage current semester backup."""
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

    # Check for existing backup of this semester
    backup_name = semester_to_filename(current_semester)
    backup_path = os.path.join(BACKUPS_DIR, backup_name)

    # Find all existing backup files to detect semester change
    existing_backups = glob.glob(os.path.join(BACKUPS_DIR, "*.json"))

    if existing_backups:
        # Check the most recent backup's semester
        latest_backup = max(existing_backups, key=os.path.getmtime)
        try:
            with open(latest_backup, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                old_mid_exam = old_data['metadata'].get('midExamStartDate')
                old_semester = get_current_semester(old_mid_exam)

            if mid_exam_start != old_mid_exam and old_semester != current_semester:
                semester_changed = True
                print(f"\n📅 Semester changed!")
                print(f"   Old: {old_mid_exam} ({old_semester})")
                print(f"   New: {mid_exam_start} ({current_semester})")
                print(f"✓ Previous backup preserved: {os.path.basename(latest_backup)}")
            else:
                print(f"✓ Same semester, updating backup...")
        except Exception as e:
            print(f"⚠️  Error reading old backup: {e}")
    else:
        semester_changed = True

    # Write current semester backup
    backup_data = {
        "metadata": metadata,
        "sections": sections
    }

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(backup_path) / 1024
    print(f"\n✓ Created/Updated: {backup_name} ({file_size:.1f} KB)")

    return backup_name, semester_changed


def manage_stable_json(metadata: Dict, sections: List[Dict]):
    """Manage stable.json — stays on current semester until final exams end.

    connect.json always has the latest API data (could be next semester mid-current).
    stable.json only updates when:
      - Same semester as current stable (daily seat/schedule changes are fine)
      - Different semester AND stable's final exams have ended

    Semester end is detected by: today > finalExamEndDate
    """
    stable_path = os.path.join(SCRIPT_DIR, "stable.json")
    incoming_semester = get_current_semester(metadata.get('midExamStartDate'))

    print("\n" + "=" * 60)
    print("Managing stable.json")
    print("=" * 60)

    if os.path.exists(stable_path):
        try:
            with open(stable_path, 'r', encoding='utf-8') as f:
                stable_data = json.load(f)

            stable_mid = stable_data['metadata'].get('midExamStartDate')
            stable_semester = get_current_semester(stable_mid)

            if incoming_semester == stable_semester:
                print(f"\n  Same semester ({stable_semester}) — updating with latest data")
            else:
                # Different semester — only switch after finals end
                final_end = stable_data['metadata'].get('finalExamEndDate')
                if final_end:
                    today = datetime.now(timezone.utc).date()
                    final_end_date = datetime.strptime(final_end, "%Y-%m-%d").date()

                    if today <= final_end_date:
                        stable_size = os.path.getsize(stable_path) / 1024
                        print(f"\n  ⏸ Frozen on {stable_semester} (finals end {final_end})")
                        print(f"  API has {incoming_semester} data, but {stable_semester} finals haven't ended")
                        print(f"  stable.json unchanged ({stable_size:.1f} KB)")
                        return

                print(f"\n  Switching: {stable_semester} → {incoming_semester} (previous finals ended)")
        except Exception as e:
            print(f"\n  ⚠️  Error reading stable.json: {e}, recreating")
    else:
        print(f"\n  Creating stable.json ({incoming_semester})")

    # Write stable.json
    stable_data = {"metadata": metadata, "sections": sections}

    with open(stable_path, 'w', encoding='utf-8') as f:
        json.dump(stable_data, f, indent=2, ensure_ascii=False)

    # Write gzipped version
    gz_path = stable_path + '.gz'
    with gzip.open(gz_path, 'wt', encoding='utf-8') as f:
        json.dump(stable_data, f, separators=(',', ':'), ensure_ascii=False)

    file_size = os.path.getsize(stable_path) / 1024
    gz_size = os.path.getsize(gz_path) / 1024
    print(f"  ✓ stable.json written ({file_size:.1f} KB, gzipped: {gz_size:.1f} KB)")


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
    print(
        f"  Regular: {regular_size:.1f} KB | Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")
    print(f"  Total exams: {metadata['totalExams']}")
    print(
        f"  Mid exams: {metadata['midExamStartDate']} to {metadata['midExamEndDate']}")
    print(
        f"  Final exams: {metadata['finalExamStartDate']} to {metadata['finalExamEndDate']}")


def main():
    """Main execution function."""
    force = '--force' in sys.argv

    print("=" * 60)
    print("MRZ Connect CDN Data Update Script")
    print("=" * 60)

    try:
        # Fetch data from API
        sections = fetch_mrz_data(force=force)

        if sections is None:
            print("\n✓ No changes detected. Exiting.")
            return 0

        # Calculate metadata first (needed for backup management)
        metadata = calculate_connect_metadata(sections)

        # Manage current semester backup
        curr_backup_name, semester_changed = manage_current_backup(
            metadata, sections)

        # Bump version (daily +1, or semester +1 & daily reset)
        version = bump_version(semester_changed)
        metadata["version"] = version

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
            json.dump(output_data, f, separators=(
                ',', ':'), ensure_ascii=False)

        # Write metadata only JSON (optimization for landing page)
        metadata_path = os.path.join(SCRIPT_DIR, "connect_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({"metadata": metadata}, f, indent=2, ensure_ascii=False)

        # Write gzipped metadata version
        metadata_gzip_path = metadata_path + '.gz'
        with gzip.open(metadata_gzip_path, 'wt', encoding='utf-8') as f:
            json.dump({"metadata": metadata}, f, separators=(
                ',', ':'), ensure_ascii=False)

        regular_size = os.path.getsize(connect_path) / 1024
        gzip_size = os.path.getsize(gzip_path) / 1024
        metadata_size = os.path.getsize(metadata_path) / 1024
        compression_ratio = ((regular_size - gzip_size) / regular_size * 100)

        print(f"\n✓ connect.json created successfully")
        print(
            f"✓ connect_metadata.json created successfully ({metadata_size:.2f} KB)")
        print(f"  Regular: {regular_size:.1f} KB")
        print(
            f"  Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")

        # Manage stable.json — stays on current semester until finals end
        manage_stable_json(metadata, sections)

        # Generate exams.json
        generate_exams_json(sections)

        # Generate backup index
        print("\n" + "=" * 60)
        print("Generating Backup Index")
        print("=" * 60)

        from generate_backup_index import generate_backup_index
        generate_backup_index()

        # Generate free/open labs CDN (always refresh — schedules can change mid-semester)
        print("\n" + "=" * 60)
        print("Generating Open Labs CDN")
        print("=" * 60)
        try:
            from generate_free_labs import generate_free_labs_json
            generate_free_labs_json()
        except Exception as e:
            print(f"⚠️  Error generating open labs: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)
        print("✓ All files generated successfully!")
        print("=" * 60)
        print(f"\nFiles:")
        print(f"  connect.json  — latest API data (always up-to-date)")
        print(f"  stable.json   — current semester (frozen until finals end)")
        print(f"  exams.json    — exam schedules")
        print(f"  open_labs.json — lab availability")
        print(f"  Backup: {curr_backup_name}")

        print("\nNext steps:")
        print("1. Review the generated JSON files")
        print("2. Commit and push to GitHub")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
