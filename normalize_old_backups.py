#!/usr/bin/env python3
"""
Normalize Old USIS JSON Backups
Converts old JSON structures from UsisDumpAnalyser repo to current CDN format
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Mapping from old field names to new field names
FIELD_MAPPING = {
    'SL': None,  # Skip this field
    'courseId': 'courseId',
    'courseCode': 'courseCode',
    'courseTitle': None,  # Not used in new format
    'courseDetails': 'sectionName',  # Extract section number
    'deptName': None,
    'empShortName': 'faculties',
    'empName': None,
    'courseCredit': 'courseCredit',
    'defaultSeatCapacity': 'capacity',
    'totalFillupSeat': 'consumedSeat',
    'availableSeat': None,  # Calculated field
    'classSchedule': 'preRegSchedule',
    'LabSchedule': 'preRegLabSchedule',
    'dayNo': None,
    'examDate': None,  # Needs parsing
    'preRequisiteCourses': 'prerequisiteCourses'
}


def extract_section_name(course_details: str) -> str:
    """Extract section name from courseDetails like 'CSE101-[01]' -> '01'"""
    if not course_details or '-[' not in course_details:
        return "01"
    
    try:
        section = course_details.split('-[')[1].rstrip(']')
        return section
    except:
        return "01"


def parse_schedule_to_class_schedules(schedule_str: str) -> List[Dict]:
    """
    Parse schedule string like 'Sunday(11:00 AM-12:20 PM-09A-07C)\\nTuesday(11:00 AM-12:20 PM-09A-07C)'
    into structured format
    """
    if not schedule_str or schedule_str.strip() == "":
        return []
    
    schedules = []
    lines = schedule_str.replace('\\n', '\n').split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '(' not in line:
            continue
            
        try:
            day = line.split('(')[0].strip().upper()
            time_part = line.split('(')[1].rstrip(')')
            
            if '-' in time_part:
                parts = time_part.split('-')
                start_time = convert_12h_to_24h(parts[0].strip())
                end_time = convert_12h_to_24h(parts[1].strip())
                
                schedules.append({
                    "startTime": start_time,
                    "endTime": end_time,
                    "day": day
                })
        except Exception as e:
            print(f"Warning: Could not parse schedule line '{line}': {e}")
            continue
    
    return schedules


def convert_12h_to_24h(time_str: str) -> str:
    """Convert '11:00 AM' to '11:00:00'"""
    try:
        time_str = time_str.strip()
        if 'AM' in time_str or 'PM' in time_str:
            dt = datetime.strptime(time_str, '%I:%M %p')
            return dt.strftime('%H:%M:%S')
        return time_str + ':00' if ':' in time_str else time_str
    except:
        return "00:00:00"


def normalize_old_section(old_section: Dict, semester: str, year: int) -> Dict:
    """Convert old section format to new CDN format"""
    
    # Generate a pseudo section ID (we don't have real ones)
    section_id = int(old_section.get('courseId', '100000'))
    
    # Extract section name
    section_name = extract_section_name(old_section.get('courseDetails', ''))
    
    # Parse capacity and consumed seats
    capacity = int(old_section.get('defaultSeatCapacity', 0)) if old_section.get('defaultSeatCapacity') else 0
    consumed_seat = int(old_section.get('totalFillupSeat', 0)) if old_section.get('totalFillupSeat') else 0
    
    # Determine section type
    section_type = "LAB" if "L" in old_section.get('courseCode', '') and old_section.get('courseCode', '').endswith('L') else "THEORY"
    
    # Parse class schedules
    class_schedules = parse_schedule_to_class_schedules(old_section.get('classSchedule', ''))
    lab_schedules = parse_schedule_to_class_schedules(old_section.get('LabSchedule', ''))
    
    # Create section schedule
    section_schedule = {
        "classPairId": None,
        "classSlotId": None,
        "finalExamDate": None,
        "finalExamStartTime": None,
        "finalExamEndTime": None,
        "midExamDate": None,
        "midExamStartTime": None,
        "midExamEndTime": None,
        "finalExamDetail": None,
        "midExamDetail": None,
        "classStartDate": None,
        "classEndDate": None,
        "classSchedules": class_schedules
    }
    
    # Build normalized section
    normalized = {
        "sectionId": section_id,
        "courseId": int(old_section.get('courseId', 100000)),
        "sectionName": section_name,
        "courseCredit": float(old_section.get('courseCredit', 3.0)) if old_section.get('courseCredit') else 3.0,
        "courseCode": old_section.get('courseCode', 'UNKNOWN'),
        "sectionType": section_type,
        "capacity": capacity,
        "consumedSeat": consumed_seat,
        "semesterSessionId": None,
        "parentSectionId": None,
        "faculties": old_section.get('empShortName', 'TBA'),
        "roomName": None,
        "roomNumber": None,
        "academicDegree": "UNDERGRADUATE",
        "sectionSchedule": section_schedule,
        "labSchedules": lab_schedules if lab_schedules else None,
        "labSectionId": None,
        "labCourseCode": None,
        "labFaculties": None,
        "labName": None,
        "labRoomName": None,
        "prerequisiteCourses": old_section.get('preRequisiteCourses', None) if old_section.get('preRequisiteCourses') else None,
        "preRegLabSchedule": old_section.get('LabSchedule', None) if old_section.get('LabSchedule') else None,
        "preRegSchedule": old_section.get('classSchedule', None) if old_section.get('classSchedule') else None
    }
    
    return normalized


def calculate_metadata(sections: List[Dict], semester: str) -> Dict:
    """Calculate metadata from sections"""
    if not sections:
        return {
            "firstSectionId": None,
            "lastSectionId": None,
            "totalSections": 0,
            "totalConsumedSeats": 0,
            "totalEmptySeats": 0,
            "totalCapacity": 0,
            "midExamStartDate": None,
            "midExamEndDate": None,
            "finalExamStartDate": None,
            "finalExamEndDate": None,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "semester": semester
        }
    
    section_ids = [s['sectionId'] for s in sections]
    total_consumed = sum(s.get('consumedSeat', 0) for s in sections)
    total_capacity = sum(s.get('capacity', 0) for s in sections)
    
    return {
        "firstSectionId": min(section_ids) if section_ids else None,
        "lastSectionId": max(section_ids) if section_ids else None,
        "totalSections": len(sections),
        "totalConsumedSeats": total_consumed,
        "totalEmptySeats": total_capacity - total_consumed,
        "totalCapacity": total_capacity,
        "midExamStartDate": None,
        "midExamEndDate": None,
        "finalExamStartDate": None,
        "finalExamEndDate": None,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "semester": semester
    }


def normalize_json_file(input_path: str, output_path: str, semester: str):
    """Normalize a single JSON file"""
    print(f"\n📄 Processing: {os.path.basename(input_path)}")
    print(f"   Semester: {semester}")
    
    # Load the old JSON
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different structures
    if isinstance(data, dict) and 'data' in data:
        # fall-24.json format: {"lastUpdated": "...", "data": [...]}
        sections_data = data['data']
        print(f"   Format: Object with 'data' array")
    elif isinstance(data, list):
        # summer-24.json, spring-25.json format: [...]
        sections_data = data
        print(f"   Format: Plain array")
    else:
        print(f"   ❌ Unknown format")
        return
    
    print(f"   Found {len(sections_data)} sections")
    
    # Extract year from semester string
    year = int(semester.split('-')[1]) if '-' in semester else 2024
    
    # Normalize all sections
    normalized_sections = []
    for old_section in sections_data:
        try:
            normalized = normalize_old_section(old_section, semester, year)
            normalized_sections.append(normalized)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not normalize section {old_section.get('courseCode', 'UNKNOWN')}: {e}")
    
    # Calculate metadata
    metadata = calculate_metadata(normalized_sections, semester)
    
    # Create output structure
    output_data = {
        "metadata": metadata,
        "sections": normalized_sections
    }
    
    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(output_path) / 1024  # KB
    print(f"   ✅ Saved: {os.path.basename(output_path)} ({file_size:.1f} KB)")
    print(f"   Normalized: {len(normalized_sections)} sections")


def main():
    """Main execution"""
    print("=" * 60)
    print("USIS JSON Backup Normalizer")
    print("=" * 60)
    
    # Define input and output directories
    input_dir = "C:/Users/mahar/temp-usis-dump"
    output_dir = "C:/Users/mahar/usis-cdn/normalized_backups"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Define files to process
    files_to_process = [
        ("summer-24.json", "Summer-2024"),
        ("fall-24.json", "Fall-2024"),
        ("spring-25.json", "Spring-2025"),
        ("summer-25.json", "Summer-2025"),
        ("fall-25.json", "Fall-2025"),
    ]
    
    # Process each file
    for filename, semester in files_to_process:
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace('.json', '_normalized.json')
        output_path = os.path.join(output_dir, output_filename)
        
        if os.path.exists(input_path):
            try:
                normalize_json_file(input_path, output_path, semester)
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
        else:
            print(f"\n⚠️  Skipping: {filename} (not found)")
    
    print("\n" + "=" * 60)
    print("✅ Normalization Complete!")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print("\nNext steps:")
    print("1. Review the normalized JSON files")
    print("2. Move them to backups/ directory with proper naming")
    print("3. Update the CDN")


if __name__ == "__main__":
    main()
