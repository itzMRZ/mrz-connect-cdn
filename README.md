# MRZ Connect CDN

[![VibeCoded](https://img.shields.io/badge/VibeCoded-2E2E2E?style=flat-square&logo=githubcopilot&logoColor=auto&labelColor=8000FF)](http://vibe-coding.urbanup.com/18529533)
[![MIT License](https://img.shields.io/badge/License-MIT-56d364?style=flat-square)](https://github.com/itzMRZ/mrz-connect-cdn/blob/main/LICENSE)
[![Website](https://img.shields.io/badge/Website-Live-58a6ff?style=flat-square)](https://connect-cdn.itzmrz.xyz/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/itzMRZ/mrz-connect-cdn)

Course and exam data API with automatic updates and backups.

## Links

- **Website**: https://connect-cdn.itzmrz.xyz/
- **Backups**: https://connect-cdn.itzmrz.xyz/backups.html
- **GitHub**: https://github.com/itzmrz/mrz-connect-cdn
- **Source Data**: https://usis-cdn.eniamza.com/connect.json

## 📡 API Endpoints

### `connect.json` - Full Course Data
```
https://connect-cdn.itzmrz.xyz/connect.json
```
**What it contains:**
- Complete course section information (all offered courses)
- Section details: course code, section name, faculty, seat availability
- Exam schedules (mid & final dates/times)
- Metadata: total sections, seat statistics, exam date ranges
- Size: ~3.4 MB (137 KB gzipped)

**Use this for:** Building course registration tools, seat availability checkers, full course catalogs

---

### `connect_metadata.json` - Metadata Only
```
https://connect-cdn.itzmrz.xyz/connect_metadata.json
```
**What it contains:**
- Just the `metadata` object from connect.json
- Stats: total sections, consumed seats, empty seats
- Exam date ranges and last updated timestamp
- Size: ~400 bytes (0.4 KB)

**Use this for:** Checking API status, displaying dashboard stats, verifying update times without downloading full data

---

### `connect_backup.json` - Backups Index
```
https://connect-cdn.itzmrz.xyz/connect_backup.json
```
**What it contains:**
- Complete list of all available backups (current + archived)
- Metadata for each backup: semester name, section count, backup timestamp
- Direct CDN links to all backup files
- Statistics: total backups, current vs archived counts

**Use this for:** Accessing historical data, comparing semesters, building backup browsers

---

### Current Semester Backup
```
https://connect-cdn.itzmrz.xyz/backups/curr_Fall2025_connect.json
```
**What it contains:**
- Full course data for the ongoing semester
- Updated weekly with latest data
- Automatically renamed to dated archive when semester ends
- Same structure as `connect.json` but frozen for current semester

**Use this for:** Accessing stable semester data, comparing with live updates

---

### Historical Backups (Archived Semesters)
```
https://connect-cdn.itzmrz.xyz/backups/20250831_2359_Summer2025_connect.json
https://connect-cdn.itzmrz.xyz/backups/20250531_2359_Spring2025_connect.json
# ... see connect_backup.json for full list
```
**What it contains:**
- Archived course data from completed semesters
- Timestamped with final exam date (YYYYMMDD_HHMM format)
- Immutable historical records
- Same structure as `connect.json`

**Use this for:** Historical analysis, semester comparisons, archival research

---

### `exams.json` - Exam Schedules Only
```
https://connect-cdn.itzmrz.xyz/exams.json
```
**What it contains:**
- Filtered exam schedule data (no seat/faculty info)
- Course codes and section names with exam dates/times
- Metadata: exam date ranges, total exam entries
- Size: ~516 KB (20 KB gzipped)

**Use this for:** Exam calendars, schedule conflict checkers, exam timetable apps

---

### `open_labs.json` - Open Lab Slots
```
https://connect-cdn.itzmrz.xyz/open_labs.json
```
**What it contains:**
- Day and time slot-based open lab room availability
- Department assignments for each lab (auto-detected from course usage)
- Open and occupied time slots for all labs
- Lab utilization statistics
- Size: ~387 KB

**Use this for:** Finding open lab rooms, scheduling lab sessions, lab utilization analysis

**Note:** Auto-generated only when semester changes (exam dates differ)

## Usage

### Regular Files

**JavaScript:**
```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json')
  .then(r => r.json())
  .then(data => console.log(data.metadata));
```

**Python:**
```python
import requests
data = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()
print(data['metadata']['totalSections'])
```

### Gzipped Files (96% smaller, faster)

**JavaScript:**
```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json.gz')
  .then(r => r.blob())
  .then(blob => blob.stream().pipeThrough(new DecompressionStream('gzip')))
  .then(stream => new Response(stream).json())
  .then(data => console.log(data.metadata));
```

**Python:**
```python
import requests, gzip, json
r = requests.get('https://connect-cdn.itzmrz.xyz/connect.json.gz')
data = json.loads(gzip.decompress(r.content))
print(data['metadata']['totalSections'])
```

## Features

- Auto-updates every 7 days via GitHub Actions
- Automatic semester-based backups when exam dates change
- Gzip compression (96% size reduction)
- Free hosting on GitHub Pages

## Run Locally

```bash
pip install requests
python update_cdn.py
```

## Credits

Data source provided by [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com/connect.json)

## License

MIT
