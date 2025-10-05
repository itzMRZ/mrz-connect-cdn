#!/usr/bin/env python3
"""
Generate connect_backup.json - Static index of all available backups
"""

import json
import os
import glob
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")
CDN_BASE_URL = "https://connect-cdn.itzmrz.xyz/backups"


def parse_backup_file(filename: str) -> dict:
    """Parse backup filename and extract metadata."""
    
    # Check for current backup: curr_Fall2025_connect.json
    curr_match = filename.startswith('curr_') and filename.endswith('_connect.json')
    if curr_match:
        semester = filename.replace('curr_', '').replace('_connect.json', '')
        
        # Load file to get section count
        filepath = os.path.join(BACKUPS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_sections = data['metadata']['totalSections']
                last_updated = data['metadata'].get('lastUpdated', '')
        except:
            total_sections = 0
            last_updated = ''
        
        return {
            "semester": semester,
            "totalSections": total_sections,
            "backupTime": last_updated,
            "cdnLink": f"{CDN_BASE_URL}/{filename}",
            "isCurrent": True,
            "filename": filename
        }
    
    # Check for archived backup: 20251104_1200_Fall2025_connect.json
    if filename.endswith('_connect.json') and not filename.startswith('curr_'):
        parts = filename.replace('_connect.json', '').split('_')
        if len(parts) >= 3:
            date = parts[0]  # YYYYMMDD
            time = parts[1]  # HHMM
            semester = parts[2]  # Fall2025
            
            # Parse date and time
            try:
                dt = datetime.strptime(f"{date}{time}", "%Y%m%d%H%M")
                backup_time = dt.isoformat() + "Z"
            except:
                backup_time = ""
            
            # Load file to get section count
            filepath = os.path.join(BACKUPS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_sections = data['metadata']['totalSections']
            except:
                total_sections = 0
            
            return {
                "semester": semester,
                "totalSections": total_sections,
                "backupTime": backup_time,
                "cdnLink": f"{CDN_BASE_URL}/{filename}",
                "isCurrent": False,
                "filename": filename
            }
    
    return None


def generate_backup_index():
    """Generate connect_backup.json with all available backups."""
    
    print("=" * 60)
    print("Generating Backup Index (connect_backup.json)")
    print("=" * 60)
    
    # Find all backup files
    backup_files = glob.glob(os.path.join(BACKUPS_DIR, "*_connect.json"))
    
    if not backup_files:
        print("⚠️  No backup files found")
        return
    
    print(f"\nFound {len(backup_files)} backup file(s)")
    
    # Parse all backups
    backups = []
    for filepath in backup_files:
        filename = os.path.basename(filepath)
        backup_info = parse_backup_file(filename)
        
        if backup_info:
            backups.append(backup_info)
            status = "CURRENT" if backup_info['isCurrent'] else "ARCHIVED"
            print(f"  ✓ {backup_info['semester']} ({status}) - {backup_info['totalSections']} sections")
    
    # Sort: current first, then by semester descending
    backups.sort(key=lambda x: (not x['isCurrent'], x['semester']), reverse=True)
    
    # Create output structure
    output = {
        "metadata": {
            "totalBackups": len(backups),
            "currentBackups": sum(1 for b in backups if b['isCurrent']),
            "archivedBackups": sum(1 for b in backups if not b['isCurrent']),
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
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
