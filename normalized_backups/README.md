# Normalized USIS Backups

This directory contains historical USIS course data that has been normalized to match the current CDN structure.

## Source

Original data from: https://github.com/itzMRZ/UsisDumpAnalyser

## What Was Done

The `normalize_old_backups.py` script converted old JSON formats into the current CDN structure:

### Old Format Issues:
- **summer-24.json**: Plain array with PascalCase fields (`SL`, `courseId`, `classSchedule`)
- **fall-24.json**: Object wrapper with `{lastUpdated, data}` structure
- **spring/summer/fall-25.json**: Plain arrays

### Normalization Process:
1. ✅ Converted field names to camelCase
2. ✅ Added metadata object with statistics
3. ✅ Parsed schedule strings into structured `classSchedules` arrays
4. ✅ Converted 12-hour times to 24-hour format
5. ✅ Extracted section names from `courseDetails` field
6. ✅ Added missing fields (with null values where data unavailable)
7. ✅ Maintained backward compatibility

## Files

| File | Semester | Sections | Size | Original Size |
|------|----------|----------|------|---------------|
| summer-24_normalized.json | Summer 2024 | 497 | 780 KB | 319 KB |
| fall-24_normalized.json | Fall 2024 | 2,349 | 3.5 MB | 1.2 MB |
| spring-25_normalized.json | Spring 2025 | 2,219 | 2.5 MB | 3.4 MB |
| summer-25_normalized.json | Summer 2025 | 2,057 | 2.3 MB | 3.2 MB |
| fall-25_normalized.json | Fall 2025 | 2,051 | 2.3 MB | 3.2 MB |

## Structure

All normalized files follow this structure:

```json
{
  "metadata": {
    "firstSectionId": 100002,
    "lastSectionId": 182113,
    "totalSections": 2100,
    "totalConsumedSeats": 63061,
    "totalEmptySeats": 4791,
    "totalCapacity": 67852,
    "midExamStartDate": null,
    "midExamEndDate": null,
    "finalExamStartDate": null,
    "finalExamEndDate": null,
    "lastUpdated": "2025-10-05T00:04:23+00:00",
    "semester": "Fall-2024"
  },
  "sections": [
    {
      "sectionId": 100002,
      "courseId": 100002,
      "sectionName": "01",
      "courseCredit": 3.0,
      "courseCode": "CSE101",
      "sectionType": "THEORY",
      "capacity": 24,
      "consumedSeat": 28,
      "semesterSessionId": null,
      "parentSectionId": null,
      "faculties": "AQZ",
      "roomName": null,
      "roomNumber": null,
      "academicDegree": "UNDERGRADUATE",
      "sectionSchedule": {
        "classPairId": null,
        "classSlotId": null,
        "finalExamDate": null,
        "finalExamStartTime": null,
        "finalExamEndTime": null,
        "midExamDate": null,
        "midExamStartTime": null,
        "midExamEndTime": null,
        "finalExamDetail": null,
        "midExamDetail": null,
        "classStartDate": null,
        "classEndDate": null,
        "classSchedules": [
          {
            "startTime": "11:00:00",
            "endTime": "12:20:00",
            "day": "SUNDAY"
          }
        ]
      },
      "labSchedules": [...],
      "labSectionId": null,
      "labCourseCode": null,
      "labFaculties": null,
      "labName": null,
      "labRoomName": null,
      "prerequisiteCourses": null,
      "preRegLabSchedule": "Saturday(2:00 PM-5:00 PM-09B-11L)",
      "preRegSchedule": "Sunday(11:00 AM-12:20 PM-09A-07C)\\nTuesday..."
    }
  ]
}
```

## Notes

- **Exam dates**: Not available in old data (set to `null`)
- **Room information**: Not available in old data (set to `null`)
- **Section IDs**: Used courseId as sectionId (no real section IDs in old data)
- **Schedule parsing**: Automatically converted string schedules to structured format
- **Time format**: Converted 12-hour to 24-hour format (e.g., "11:00 AM" → "11:00:00")

## Usage

These files can be used as:
1. Historical backups for the CDN
2. Data for analysis and comparison
3. Testing data for applications

To move to CDN backups directory, rename with timestamp:
```bash
# Example
mv summer-24_normalized.json ../backups/20240501_0000_Summer2024_connect.json
```

## Credits

- Original data source: [@eniamza](https://github.com/eniamza)
- Normalization script: `normalize_old_backups.py`
- CDN: https://connect-cdn.itzmrz.xyz/
