# Free Labs CDN Guide

## Overview
The Free Labs CDN provides real-time information about available lab rooms across campus, showing free and occupied time slots for each lab.

## Access
```
https://connect-cdn.itzmrz.xyz/free_labs.json
```

## Features

### 🔍 Smart Lab Detection
- Automatically detects all lab rooms from course schedules
- Identifies rooms ending with "L" or containing "LAB" in their name
- Currently tracking **50 lab rooms**

### 🏢 Department Assignment
- Auto-detects which departments use each lab
- Based on course codes (e.g., CSE251L → CSE department)
- Multi-department labs show all departments using them

### ⏰ Time Slot Analysis
- 7 time slots per day:
  - 08:00 AM - 09:20 AM
  - 09:30 AM - 10:50 AM
  - 11:00 AM - 12:20 PM
  - 12:30 PM - 01:50 PM
  - 02:00 PM - 03:20 PM
  - 03:30 PM - 04:50 PM
  - 05:00 PM - 06:20 PM

- 6 days covered: Saturday - Thursday

### 📊 Statistics
- Total free slots across all labs
- Lab utilization percentage
- Free vs occupied slot breakdown
- Per-lab statistics

## Data Structure

### Metadata
```json
{
  "metadata": {
    "semester": "Fall2025",
    "totalLabs": 50,
    "totalFreeSlots": 836,
    "totalOccupiedSlots": 1264,
    "averageUtilization": 60.19,
    "timeSlots": [...],
    "days": [...],
    "lastUpdated": "2025-10-05T00:56:29Z",
    "sourceDataUpdated": "2025-10-05T00:39:15Z"
  }
}
```

### Lab Entry
```json
{
  "labRoom": "09B-08L",
  "departments": ["CSE"],
  "totalSlots": 42,
  "freeSlotCount": 8,
  "occupiedSlotCount": 34,
  "utilizationPercent": 80.95,
  "freeSlots": [
    {
      "day": "SATURDAY",
      "startTime": "17:00:00",
      "endTime": "18:20:00"
    }
  ],
  "occupiedSlots": [
    {
      "day": "SATURDAY",
      "startTime": "08:00:00",
      "endTime": "09:20:00",
      "courseCode": "CSE251L",
      "sectionName": "06B",
      "department": "CSE"
    }
  ]
}
```

## Generation Logic

### When Does It Run?
The free labs analyzer **only runs when the semester changes**, detected by:
- Different mid exam start dates
- New semester detected in backup system

### Why Semester-Based?
- Lab schedules are fixed for the entire semester
- Saves computational resources (no need to regenerate weekly)
- Reduces API calls and processing time
- Data remains valid throughout the semester

### Manual Generation
To regenerate manually:
```bash
python generate_free_labs.py
```

## Use Cases

### 1. Find Free Lab Rooms
```javascript
fetch('https://connect-cdn.itzmrz.xyz/free_labs.json')
  .then(r => r.json())
  .then(data => {
    const freeNow = data.labs.filter(lab => 
      lab.freeSlotCount > 0
    );
    console.log(`${freeNow.length} labs have free slots`);
  });
```

### 2. Find Labs by Department
```python
import requests

data = requests.get('https://connect-cdn.itzmrz.xyz/free_labs.json').json()

cse_labs = [lab for lab in data['labs'] if 'CSE' in lab['departments']]
print(f"CSE Department uses {len(cse_labs)} labs")
```

### 3. Find Free Slots on Specific Day
```javascript
const findFreeSlots = (day) => {
  return data.labs.map(lab => ({
    room: lab.labRoom,
    freeSlots: lab.freeSlots.filter(slot => slot.day === day)
  })).filter(lab => lab.freeSlots.length > 0);
};

const sundayFree = findFreeSlots('SUNDAY');
```

### 4. Lab Utilization Analysis
```python
# Find most/least utilized labs
labs = data['labs']
most_utilized = max(labs, key=lambda x: x['utilizationPercent'])
least_utilized = min(labs, key=lambda x: x['utilizationPercent'])

print(f"Most busy: {most_utilized['labRoom']} ({most_utilized['utilizationPercent']}%)")
print(f"Least busy: {least_utilized['labRoom']} ({least_utilized['utilizationPercent']}%)")
```

## Current Statistics (Fall 2025)

- **Total Labs:** 50
- **Total Free Slots:** 836
- **Total Occupied Slots:** 1,264
- **Average Utilization:** 60.2%
- **Total Possible Slots:** 2,100 (50 labs × 42 slots)

## Algorithm Details

### Lab Detection
1. Scan all sections in `connect.json`
2. Look for:
   - Theory sections with `labSchedules` and `labRoomName`
   - Standalone LAB sections with room names ending in "L"
3. Extract room name, course code, and schedule

### Department Detection
1. Extract course code (e.g., "CSE251L")
2. Remove trailing "L" → "CSE251"
3. Extract alphabetic prefix → "CSE"
4. Track all unique departments per lab

### Overlap Detection
1. For each lab and each day
2. Check all 7 time slots
3. Compare slot time range with occupied schedules
4. Use interval overlap algorithm:
   - Overlap if: `slot_start < occupied_end AND occupied_start < slot_end`
5. Mark as free if no overlaps found

### Utilization Calculation
```
Utilization % = (Occupied Slots / Total Slots) × 100
Total Slots = 6 days × 7 time slots = 42 slots per lab
```

## Limitations

### 1. Lab Room Detection
- Only detects rooms ending with "L" or containing "LAB"
- May miss labs with unconventional naming

### 2. Department Assignment
- Based on course code prefixes
- May not capture all department collaborations
- Multi-departmental courses assigned to primary department

### 3. Time Slot Assumptions
- Fixed 7 time slots may not cover all actual class times
- Some labs may have sessions outside standard slots
- No Friday or weekend coverage

### 4. Data Accuracy
- Depends on source data accuracy from `connect.json`
- Lab schedule changes mid-semester not reflected until next semester

## Future Enhancements

### Potential Features
1. **Real-time availability** - Check current time against schedule
2. **Room capacity tracking** - Add seat count for each lab
3. **Equipment information** - List available equipment per lab
4. **Booking integration** - Allow lab reservations
5. **Historical trends** - Track utilization over semesters
6. **Mobile app support** - Dedicated lab finder app
7. **Email notifications** - Alert for newly available slots

### Optimization Ideas
1. Compress JSON with gzip (like other CDN files)
2. Add filtering API parameters
3. Cache popular queries
4. Add WebSocket for real-time updates

## Contributing

To improve lab detection or add features:
1. Edit `generate_free_labs.py`
2. Test with `python generate_free_labs.py`
3. Verify output structure
4. Submit PR to repository

## Credits

- Data source: [@eniamza](https://github.com/eniamza)
- Original CDN: [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com)
- Free Labs Analyzer: Part of MRZ Connect CDN

---

**Last Updated:** October 5, 2025  
**Current Semester:** Fall 2025  
**Status:** Production Ready ✅
