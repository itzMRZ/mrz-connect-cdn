#!/usr/bin/env python3
"""
Free Labs Analyzer - Generates free lab slots CDN
Analyzes lab room usage and identifies free time slots for each lab.
"""

import json
import os
import gzip
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Set, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define time slots
TIME_SLOTS = [
    ("08:00:00", "09:20:00"),
    ("09:30:00", "10:50:00"),
    ("11:00:00", "12:20:00"),
    ("12:30:00", "13:50:00"),
    ("14:00:00", "15:20:00"),
    ("15:30:00", "16:50:00"),
    ("17:00:00", "18:20:00"),
]

DAYS = ["SATURDAY", "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]


def parse_time(time_str: str) -> Tuple[int, int]:
    """Parse time string to (hour, minute) tuple."""
    try:
        h, m, s = map(int, time_str.split(':'))
        return (h, m)
    except:
        return (0, 0)


def time_overlaps(start1: str, end1: str, start2: str, end2: str) -> bool:
    """Check if two time ranges overlap."""
    s1 = parse_time(start1)
    e1 = parse_time(end1)
    s2 = parse_time(start2)
    e2 = parse_time(end2)

    # Check overlap: start1 < end2 and start2 < end1
    return s1 < e2 and s2 < e1


def extract_department_from_course(course_code: str) -> str:
    """Extract department from course code (e.g., CSE251L -> CSE)."""
    if not course_code:
        return "UNKNOWN"

    # Remove trailing L (for lab courses)
    code = course_code.rstrip('L')

    # Extract letters from beginning
    dept = ''
    for char in code:
        if char.isalpha():
            dept += char
        else:
            break

    return dept if dept else "UNKNOWN"


def is_lab_room(room_name: str) -> bool:
    """Check if a room is a lab based on naming convention."""
    if not room_name:
        return False
    return room_name.endswith('L') or 'LAB' in room_name.upper()


def analyze_lab_usage(sections: List[Dict]) -> tuple:
    """Analyze lab room usage from sections data."""

    # Track occupied slots for each lab room
    # Structure: {room_name: {day: [(start_time, end_time, course_code, section_name)]}}
    lab_occupancy = defaultdict(lambda: defaultdict(list))

    # Track departments using each lab
    lab_departments = defaultdict(set)

    print("Analyzing lab usage...")

    for section in sections:
        # Check theory sections with lab schedules
        if section.get('labSchedules') and section.get('labRoomName'):
            lab_room = section['labRoomName']
            course_code = section.get('labCourseCode') or section.get('courseCode')
            dept = extract_department_from_course(course_code)

            lab_departments[lab_room].add(dept)

            for schedule in section['labSchedules']:
                day = schedule.get('day')
                start_time = schedule.get('startTime')
                end_time = schedule.get('endTime')

                if day and start_time and end_time:
                    lab_occupancy[lab_room][day].append({
                        'startTime': start_time,
                        'endTime': end_time,
                        'courseCode': course_code,
                        'sectionName': section.get('sectionName'),
                        'department': dept
                    })

        # Check standalone lab sections
        if section.get('sectionType') == 'LAB':
            room_name = section.get('roomName') or section.get('roomNumber')

            # Only process if it looks like a lab room
            if room_name and is_lab_room(room_name):
                course_code = section.get('courseCode')
                dept = extract_department_from_course(course_code)

                lab_departments[room_name].add(dept)

                schedules = section.get('sectionSchedule', {}).get('classSchedules', [])
                for schedule in schedules:
                    day = schedule.get('day')
                    start_time = schedule.get('startTime')
                    end_time = schedule.get('endTime')

                    if day and start_time and end_time:
                        lab_occupancy[room_name][day].append({
                            'startTime': start_time,
                            'endTime': end_time,
                            'courseCode': course_code,
                            'sectionName': section.get('sectionName'),
                            'department': dept
                        })

    print(f"✓ Found {len(lab_occupancy)} lab rooms in use")

    return lab_occupancy, lab_departments


def find_free_slots(lab_occupancy: Dict, lab_departments: Dict) -> Dict:
    """Find free time slots organized by day and time slot."""

    # Structure: {day: {slot: {free: [{lab, depts}], occupied: [{lab, course, dept}]}}}
    slots_data = {}

    for day in DAYS:
        slots_data[day] = {}

        for slot_start, slot_end in TIME_SLOTS:
            slot_key = f"{slot_start}-{slot_end}"
            slots_data[day][slot_key] = {
                'startTime': slot_start,
                'endTime': slot_end,
                'freeLabs': [],
                'occupiedLabs': []
            }

            # Check each lab for this day/slot
            for lab_room in sorted(lab_occupancy.keys()):
                occupied_times = lab_occupancy[lab_room].get(day, [])
                is_free = True
                occupied_info = None

                # Check if this slot overlaps with any occupied time
                for occupied in occupied_times:
                    if time_overlaps(slot_start, slot_end,
                                   occupied['startTime'], occupied['endTime']):
                        is_free = False
                        occupied_info = occupied
                        break

                if is_free:
                    slots_data[day][slot_key]['freeLabs'].append({
                        'labRoom': lab_room,
                        'departments': sorted(list(lab_departments[lab_room]))
                    })
                else:
                    slots_data[day][slot_key]['occupiedLabs'].append({
                        'labRoom': lab_room,
                        'departments': sorted(list(lab_departments[lab_room])),
                        'courseCode': occupied_info['courseCode'],
                        'sectionName': occupied_info['sectionName'],
                        'department': occupied_info['department']
                    })

    return slots_data


def generate_free_labs_json():
    """Main function to generate free labs JSON."""

    print("=" * 60)
    print("Free Labs Analyzer")
    print("=" * 60)

    # Load current connect.json
    connect_path = os.path.join(SCRIPT_DIR, "connect.json")

    if not os.path.exists(connect_path):
        print("✗ connect.json not found. Run update_cdn.py first.")
        return False

    print("\nLoading connect.json...")
    with open(connect_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sections = data.get('sections', [])
    metadata = data.get('metadata', {})

    print(f"✓ Loaded {len(sections)} sections")

    # Analyze lab usage
    lab_occupancy, lab_departments = analyze_lab_usage(sections)

    # Find free slots
    print("\nFinding free time slots...")
    slots_data = find_free_slots(lab_occupancy, lab_departments)

    # Calculate overall statistics
    total_labs = len(lab_occupancy)
    total_free_count = 0
    total_occupied_count = 0

    for day in slots_data:
        for slot_key in slots_data[day]:
            total_free_count += len(slots_data[day][slot_key]['freeLabs'])
            total_occupied_count += len(slots_data[day][slot_key]['occupiedLabs'])

    total_possible = total_labs * len(DAYS) * len(TIME_SLOTS)
    avg_utilization = (total_occupied_count / total_possible * 100) if total_possible > 0 else 0

    # Create output structure
    output = {
        'metadata': {
            'semester': get_current_semester(metadata.get('midExamStartDate')),
            'totalLabs': total_labs,
            'totalFreeSlots': total_free_count,
            'totalOccupiedSlots': total_occupied_count,
            'averageUtilization': round(avg_utilization, 2),
            'timeSlots': TIME_SLOTS,
            'days': DAYS,
            'lastUpdated': datetime.now(timezone.utc).isoformat(),
            'sourceDataUpdated': metadata.get('lastUpdated')
        },
        'schedule': slots_data
    }

    # Write to file
    output_path = os.path.join(SCRIPT_DIR, "open_labs.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Write gzipped version
    gzip_path = output_path + '.gz'
    with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
        json.dump(output, f, separators=(',', ':'), ensure_ascii=False)

    file_size = os.path.getsize(output_path) / 1024
    gzip_size = os.path.getsize(gzip_path) / 1024

    print(f"\n\u2713 open_labs.json created ({file_size:.1f} KB, gzipped {gzip_size:.1f} KB)")
    print(f"  Total labs: {total_labs}")
    print(f"  Total free slot entries: {total_free_count}")
    print(f"  Average utilization: {avg_utilization:.1f}%")
    print("\n" + "=" * 60)

    return True


def get_current_semester(mid_exam_start: str) -> str:
    """Determine current semester based on mid exam start date."""
    if not mid_exam_start:
        return "Unknown"

    try:
        date = datetime.strptime(mid_exam_start, "%Y-%m-%d")
        month = date.month
        year = date.year

        if 1 <= month <= 4:
            return f"Spring{year}"
        elif 5 <= month <= 8:
            return f"Summer{year}"
        else:
            return f"Fall{year}"
    except:
        return "Unknown"


if __name__ == "__main__":
    success = generate_free_labs_json()
    exit(0 if success else 1)
