#!/usr/bin/env python3
"""
MRZ Connect CDN Data Update Script
Fetches course data from MRZ Connect API and generates static CDN files with metadata.
"""

import json
import os
import gzip
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


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
            "finalExamDate": final_date,
            "finalExamTime": final_time
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
        
        # Generate both JSON files
        generate_connect_json(sections)
        generate_exams_json(sections)
        
        print("\n" + "=" * 60)
        print("✓ All files generated successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the generated JSON files")
        print("2. Open index.html in a browser to test")
        print("3. Commit and push to GitHub")
        print("4. Enable GitHub Pages in repository settings")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
