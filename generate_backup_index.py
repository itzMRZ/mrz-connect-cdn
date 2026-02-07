#!/usr/bin/env python3
"""
Generate connect_backup.json - Static index of all available backups.
Backup files use clean naming: spring2026.json, fall2025.json, etc.
"""

import json
import os
import re
import glob
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")
CDN_BASE_URL = "https://connect-cdn.itzmrz.xyz/backups"
CDN_ROOT_URL = "https://connect-cdn.itzmrz.xyz"

# Pattern: spring2026.json, fall2024.json, summer2025.json
BACKUP_PATTERN = re.compile(r'^(spring|summer|fall)(\d{4})\.json$', re.IGNORECASE)


def get_current_semester_name() -> str:
    """Read current semester from connect_metadata.json."""
    try:
        meta_path = os.path.join(SCRIPT_DIR, "connect_metadata.json")
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        mid = data['metadata'].get('midExamStartDate')
        if mid:
            date = datetime.strptime(mid, "%Y-%m-%d")
            m, y = date.month, date.year
            if 1 <= m <= 4:
                return f"Spring{y}"
            elif 5 <= m <= 8:
                return f"Summer{y}"
            else:
                return f"Fall{y}"
    except Exception:
        pass
    return ""


def parse_backup_file(filename: str, current_semester: str) -> dict:
    """Parse backup filename and extract metadata."""
    match = BACKUP_PATTERN.match(filename)
    if not match:
        return None

    season = match.group(1).capitalize()
    year = match.group(2)
    semester = f"{season}{year}"

    # Load file to get section count and backup time
    filepath = os.path.join(BACKUPS_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            total_sections = data['metadata']['totalSections']
            last_updated = data['metadata'].get('lastUpdated', '')
    except Exception:
        total_sections = 0
        last_updated = ''

    is_current = (semester == current_semester)

    return {
        "semester": semester,
        "totalSections": total_sections,
        "backupTime": last_updated,
        "cdnLink": f"{CDN_BASE_URL}/{filename}",
        "isCurrent": is_current,
        "filename": filename
    }


def generate_backup_index():
    """Generate connect_backup.json with all available backups."""

    print("=" * 60)
    print("Generating Backup Index (connect_backup.json)")
    print("=" * 60)

    current_semester = get_current_semester_name()
    print(f"\nCurrent semester: {current_semester or 'Unknown'}")

    # Find all backup files
    backup_files = glob.glob(os.path.join(BACKUPS_DIR, "*.json"))

    if not backup_files:
        print("⚠️  No backup files found")
        return

    print(f"Found {len(backup_files)} backup file(s)")

    # Parse all backups
    backups = []
    for filepath in backup_files:
        filename = os.path.basename(filepath)
        backup_info = parse_backup_file(filename, current_semester)

        if backup_info:
            backups.append(backup_info)
            status = "CURRENT" if backup_info['isCurrent'] else "ARCHIVED"
            print(f"  ✓ {backup_info['semester']} ({status}) - {backup_info['totalSections']} sections")

    # Sort: current first, then by backup time descending
    backups.sort(
        key=lambda b: (1 if b['isCurrent'] else 0, b.get('backupTime', '') or ''),
        reverse=True
    )

    # Find the current backup info
    current_backup = next((b for b in backups if b['isCurrent']), None)

    # Create output structure
    output = {
        "metadata": {
            "totalBackups": len(backups),
            "currentSemester": current_backup['semester'] if current_backup else None,
            "stableUrl": f"{CDN_ROOT_URL}/stable.json",
            "currentBackups": sum(1 for b in backups if b['isCurrent']),
            "archivedBackups": sum(1 for b in backups if not b['isCurrent']),
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "cdnBaseUrl": CDN_BASE_URL
        },
        "backups": backups
    }

    # Write to connect_backup.json
    output_path = os.path.join(SCRIPT_DIR, "connect_backup.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path) / 1024

    print(f"\n✓ connect_backup.json created ({file_size:.1f} KB)")
    print(f"  Total backups: {output['metadata']['totalBackups']}")
    print(f"  Current: {output['metadata']['currentBackups']}")
    print(f"  Archived: {output['metadata']['archivedBackups']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    generate_backup_index()
