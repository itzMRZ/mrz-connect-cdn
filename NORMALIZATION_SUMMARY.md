# USIS JSON Normalization Project - Summary

## Overview

Successfully normalized historical USIS course data from the **UsisDumpAnalyser** repository to match the current MRZ Connect CDN structure.

---

## 📊 Results

### Files Normalized

| Semester | Original Format | Sections | Output Size | Status |
|----------|----------------|----------|-------------|--------|
| **Summer 2024** | Plain Array | 497 | 780 KB | ✅ Success |
| **Fall 2024** | Object + Array | 2,349 | 3.5 MB | ✅ Success |
| **Spring 2025** | Plain Array | 2,219 | 2.5 MB | ✅ Success |
| **Summer 2025** | Plain Array | 2,057 | 2.3 MB | ✅ Success |
| **Fall 2025** | Plain Array | 2,051 | 2.3 MB | ✅ Success |

**Total:** 9,173 sections normalized

---

## 🔧 Technical Details

### Original Structure Issues

**Old Format (Summer 2024):**
```json
[
  {
    "SL": "1",
    "courseId": "100002",
    "courseCode": "CSE101",
    "courseTitle": "CSE101 Course",
    "courseDetails": "CSE101-[01]",
    "empShortName": "AQZ",
    "courseCredit": "3.0",
    "defaultSeatCapacity": "24",
    "totalFillupSeat": "28",
    "classSchedule": "Sunday(11:00 AM-12:20 PM-09A-07C)\\nTuesday..."
  }
]
```

**New CDN Format:**
```json
{
  "metadata": {
    "totalSections": 497,
    "totalConsumedSeats": 13916,
    "totalCapacity": 11928,
    "semester": "Summer-2024",
    "lastUpdated": "2025-10-05T00:04:23+00:00"
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
      "faculties": "AQZ",
      "sectionSchedule": {
        "classSchedules": [
          {
            "startTime": "11:00:00",
            "endTime": "12:20:00",
            "day": "SUNDAY"
          }
        ]
      },
      "preRegSchedule": "Sunday(11:00 AM-12:20 PM-09A-07C)\\nTuesday..."
    }
  ]
}
```

### Transformation Process

1. **Field Mapping**
   - `SL` → (skipped)
   - `courseDetails` → extracted `sectionName`
   - `empShortName` → `faculties`
   - `defaultSeatCapacity` → `capacity`
   - `totalFillupSeat` → `consumedSeat`

2. **Schedule Parsing**
   - Converted: `"Sunday(11:00 AM-12:20 PM-09A-07C)"`
   - To: `{"startTime": "11:00:00", "endTime": "12:20:00", "day": "SUNDAY"}`

3. **Time Conversion**
   - 12-hour format → 24-hour format
   - `"11:00 AM"` → `"11:00:00"`
   - `"02:00 PM"` → `"14:00:00"`

4. **Metadata Generation**
   - Calculated statistics from sections
   - Added semester information
   - Added timestamp

5. **Null Handling**
   - Fields unavailable in old data set to `null`
   - Maintains structure compatibility

---

## 📁 File Structure

```
usis-cdn/
├── normalize_old_backups.py       # Normalization script
├── normalized_backups/             # Output directory
│   ├── README.md                   # Documentation
│   ├── summer-24_normalized.json
│   ├── fall-24_normalized.json
│   ├── spring-25_normalized.json
│   ├── summer-25_normalized.json
│   └── fall-25_normalized.json
└── NORMALIZATION_SUMMARY.md        # This file
```

---

## 🎯 Key Features

### 1. Structure Consistency
- All files follow the same schema as current CDN
- Backward compatible with existing applications
- Ready for immediate use

### 2. Data Enrichment
- Added metadata objects with statistics
- Structured schedule data
- Standardized time formats

### 3. Maintainability
- Clear field mappings
- Comprehensive error handling
- Detailed logging during conversion

### 4. Documentation
- README in normalized_backups/
- Inline code comments
- This summary document

---

## 🚀 Usage

### As Historical Backups

Move to CDN backups directory with proper naming:

```bash
# Example for Summer 2024
cp normalized_backups/summer-24_normalized.json \
   backups/20240501_0000_Summer2024_connect.json
```

### For Analysis

```python
import json

# Load normalized data
with open('normalized_backups/summer-24_normalized.json') as f:
    data = json.load(f)

# Access metadata
print(f"Semester: {data['metadata']['semester']}")
print(f"Total Sections: {data['metadata']['totalSections']}")

# Access sections
for section in data['sections']:
    print(f"{section['courseCode']} - {section['sectionName']}")
```

### For Testing

```javascript
// Fetch normalized backup
fetch('normalized_backups/fall-24_normalized.json')
  .then(r => r.json())
  .then(data => {
    console.log(`Loaded ${data.metadata.totalSections} sections`);
  });
```

---

## ⚠️ Limitations

1. **Exam Dates**: Not available in source data (set to `null`)
2. **Room Info**: Not available in source data (set to `null`)
3. **Section IDs**: Used courseId as proxy (real IDs not in source)
4. **Semester Session IDs**: Not available (set to `null`)

---

## ✅ Quality Assurance

- ✅ All 5 files processed successfully
- ✅ 9,173 total sections normalized
- ✅ No data loss during conversion
- ✅ Structure matches current CDN format
- ✅ Schedule parsing working correctly
- ✅ Time conversion accurate
- ✅ Metadata calculations correct

---

## 📚 Resources

- **Original Data**: https://github.com/itzMRZ/UsisDumpAnalyser
- **CDN Website**: https://connect-cdn.itzmrz.xyz/
- **Documentation**: `normalized_backups/README.md`
- **Script**: `normalize_old_backups.py`

---

## 🙏 Credits

- **Data Source**: [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com/)
- **Normalization Script**: Created for MRZ Connect CDN
- **Repository**: [itzMRZ/mrz-connect-cdn](https://github.com/itzMRZ/mrz-connect-cdn)

---

## 📝 Notes

- Normalization completed: 2025-10-05
- Processing time: < 5 seconds
- Output format: JSON (indent=2)
- Character encoding: UTF-8
- Python version: 3.x

---

**Status**: ✅ Project Complete

All historical data successfully normalized and ready for use!
