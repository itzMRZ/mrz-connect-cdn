#!/usr/bin/env python3
"""
Free Labs Analyzer - Generates free lab slots CDN
Analyzes lab room usage and identifies free time slots for each lab.
"""

import json
import os
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


def analyze_lab_usage(sections: List[Dict]) -> Dict:
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


def find_free_slots(lab_occupancy: Dict, lab_departments: Dict) -> List[Dict]:
    """Find free time slots for each lab."""
    
    free_labs = []
    
    for lab_room in sorted(lab_occupancy.keys()):
        lab_data = {
            'labRoom': lab_room,
            'departments': sorted(list(lab_departments[lab_room])),
            'freeSlots': [],
            'occupiedSlots': []
        }
        
        # Analyze each day
        for day in DAYS:
            occupied_times = lab_occupancy[lab_room].get(day, [])
            
            # Check each time slot
            for slot_start, slot_end in TIME_SLOTS:
                is_free = True
                
                # Check if this slot overlaps with any occupied time
                for occupied in occupied_times:
                    if time_overlaps(slot_start, slot_end, 
                                   occupied['startTime'], occupied['endTime']):
                        is_free = False
                        
                        # Add to occupied slots
                        lab_data['occupiedSlots'].append({
                            'day': day,
                            'startTime': slot_start,
                            'endTime': slot_end,
                            'courseCode': occupied['courseCode'],
                            'sectionName': occupied['sectionName'],
                            'department': occupied['department']
                        })
                        break
                
                if is_free:
                    lab_data['freeSlots'].append({
                        'day': day,
                        'startTime': slot_start,
                        'endTime': slot_end
                    })
        
        # Calculate statistics
        total_slots = len(DAYS) * len(TIME_SLOTS)
        lab_data['totalSlots'] = total_slots
        lab_data['freeSlotCount'] = len(lab_data['freeSlots'])
        lab_data['occupiedSlotCount'] = len(lab_data['occupiedSlots'])
        lab_data['utilizationPercent'] = round(
            (lab_data['occupiedSlotCount'] / total_slots * 100), 2
        )
        
        free_labs.append(lab_data)
    
    # Sort by lab room name
    free_labs.sort(key=lambda x: x['labRoom'])
    
    return free_labs


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
    free_labs = find_free_slots(lab_occupancy, lab_departments)
    
    # Calculate overall statistics
    total_labs = len(free_labs)
    total_free_slots = sum(lab['freeSlotCount'] for lab in free_labs)
    total_occupied_slots = sum(lab['occupiedSlotCount'] for lab in free_labs)
    avg_utilization = sum(lab['utilizationPercent'] for lab in free_labs) / total_labs if total_labs > 0 else 0
    
    # Create output structure
    output = {
        'metadata': {
            'semester': get_current_semester(metadata.get('midExamStartDate')),
            'totalLabs': total_labs,
            'totalFreeSlots': total_free_slots,
            'totalOccupiedSlots': total_occupied_slots,
            'averageUtilization': round(avg_utilization, 2),
            'timeSlots': TIME_SLOTS,
            'days': DAYS,
            'lastUpdated': datetime.now(timezone.utc).isoformat(),
            'sourceDataUpdated': metadata.get('lastUpdated')
        },
        'labs': free_labs
    }
    
    # Write to file
    output_path = os.path.join(SCRIPT_DIR, "free_labs.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(output_path) / 1024
    
    print(f"\n✓ free_labs.json created ({file_size:.1f} KB)")
    print(f"  Total labs: {total_labs}")
    print(f"  Total free slots: {total_free_slots}")
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
