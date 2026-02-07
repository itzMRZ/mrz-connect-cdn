# MRZ Connect CDN

[![VibeCoded](https://img.shields.io/badge/VibeCoded-2E2E2E?style=flat-square&logo=githubcopilot&logoColor=auto&labelColor=8000FF)](http://vibe-coding.urbanup.com/18529533)
[![MIT License](https://img.shields.io/badge/License-MIT-56d364?style=flat-square)](https://github.com/itzMRZ/mrz-connect-cdn/blob/main/LICENSE)
[![Website](https://img.shields.io/badge/Website-Live-58a6ff?style=flat-square)](https://connect-cdn.itzmrz.xyz/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/itzMRZ/mrz-connect-cdn)

Open-source JSON API serving BRAC University course data, exam schedules, and lab availability. Automatically updated daily via GitHub Actions and hosted on GitHub Pages.

**Website:** https://connect-cdn.itzmrz.xyz

---

## Quick Start

Need course data? Just fetch one URL:

```js
// Get all current semester data
const data = await fetch('https://connect-cdn.itzmrz.xyz/latest.json').then(r => r.json());
console.log(data.metadata.totalSections); // e.g. 2353
console.log(data.sections[0]);            // first course section
```

```python
import requests
data = requests.get('https://connect-cdn.itzmrz.xyz/latest.json').json()
print(data['metadata']['totalSections'])  # e.g. 2353
```

That's it. `latest.json` always points to the current semester — no hardcoding needed.

---

## All API Endpoints

| Endpoint | Description | Size |
|----------|-------------|------|
| [`/connect.json`](https://connect-cdn.itzmrz.xyz/connect.json) | Full course data with metadata (primary file) | ~3.4 MB |
| [`/latest.json`](https://connect-cdn.itzmrz.xyz/latest.json) | Current semester alias — always points to current data | ~3.4 MB |
| [`/exams.json`](https://connect-cdn.itzmrz.xyz/exams.json) | Exam schedules only (mid + final dates/times) | ~516 KB |
| [`/open_labs.json`](https://connect-cdn.itzmrz.xyz/open_labs.json) | Lab room availability by day and time slot | ~387 KB |
| [`/connect_metadata.json`](https://connect-cdn.itzmrz.xyz/connect_metadata.json) | Lightweight stats (section count, seats, exam ranges) | ~400 B |
| [`/connect_backup.json`](https://connect-cdn.itzmrz.xyz/connect_backup.json) | Index of all semester backups with CDN links | ~2 KB |
| [`/backups/{season}{year}.json`](https://connect-cdn.itzmrz.xyz/backups/spring2026.json) | Individual semester archives (e.g. `spring2026.json`) | ~3.4 MB |

Every JSON file also has a `.gz` variant (append `.gz` to the URL) for ~96% smaller downloads.

### Which file should I use?

- **Building a course tool?** → `/connect.json` or `/latest.json` (identical for current semester)
- **Only need exams?** → `/exams.json` (much lighter)
- **Finding open labs?** → `/open_labs.json`
- **Just need stats?** → `/connect_metadata.json` (~400 bytes vs 3.4 MB)
- **Want historical data?** → `/connect_backup.json` to discover all semesters, then fetch `/backups/{season}{year}.json`
- **Stable current-semester link?** → `/latest.json` (no need to figure out semester names)

---

## Data Structure

### connect.json / latest.json

```json
{
  "metadata": {
    "totalSections": 2353,
    "totalConsumedSeats": 48295,
    "totalEmptySeats": 22607,
    "midExamStartDate": "2026-03-07",
    "midExamEndDate": "2026-03-19",
    "finalExamStartDate": "2026-05-09",
    "finalExamEndDate": "2026-05-21",
    "lastUpdated": "2026-02-07T06:00:00.000Z",
    "version": "2.3.1"
  },
  "sections": [
    {
      "courseCode": "CSE110",
      "sectionName": "01",
      "facultyName": "Dr. Someone",
      "totalSeat": 40,
      "consumedSeat": 35,
      "emptySeat": 5,
      "classDay": "ST",
      "classTime": "08:00 AM-09:20 AM",
      "classRoom": "UB40203",
      "midExamDate": "2026-03-10",
      "midExamTime": "09:00 AM",
      "finalExamDate": "2026-05-10",
      "finalExamTime": "09:00 AM"
    }
  ]
}
```

### exams.json

```json
{
  "metadata": {
    "totalExams": 2353,
    "midExamStartDate": "2026-03-07",
    "midExamEndDate": "2026-03-19",
    "finalExamStartDate": "2026-05-09",
    "finalExamEndDate": "2026-05-21"
  },
  "exams": [
    {
      "courseCode": "CSE110",
      "sectionName": "01",
      "midExamDate": "2026-03-10",
      "midExamTime": "09:00 AM",
      "finalExamDate": "2026-05-10",
      "finalExamTime": "09:00 AM"
    }
  ]
}
```

### connect_metadata.json

```json
{
  "metadata": {
    "totalSections": 2353,
    "totalConsumedSeats": 48295,
    "totalEmptySeats": 22607,
    "midExamStartDate": "2026-03-07",
    "midExamEndDate": "2026-03-19",
    "finalExamStartDate": "2026-05-09",
    "finalExamEndDate": "2026-05-21",
    "lastUpdated": "2026-02-07T06:00:00.000Z",
    "version": "2.3.1"
  }
}
```

### connect_backup.json

```json
{
  "metadata": {
    "totalBackups": 6,
    "currentSemester": "Spring2026",
    "latestBackup": "https://connect-cdn.itzmrz.xyz/latest.json",
    "currentBackups": 1,
    "archivedBackups": 5,
    "cdnBaseUrl": "https://connect-cdn.itzmrz.xyz/backups"
  },
  "backups": [
    {
      "semester": "Spring2026",
      "totalSections": 2353,
      "backupTime": "2026-02-07T06:00:00.000Z",
      "cdnLink": "https://connect-cdn.itzmrz.xyz/backups/spring2026.json",
      "isCurrent": true,
      "filename": "spring2026.json"
    }
  ]
}
```

---

## Gzip Compression

Every JSON file has a `.gz` version for significantly smaller downloads:

| File | Regular | Gzipped | Savings |
|------|---------|---------|---------|
| connect.json | ~3.4 MB | ~137 KB | 96% |
| exams.json | ~516 KB | ~20 KB | 96% |
| open_labs.json | ~387 KB | ~15 KB | 96% |

### Using gzipped files

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

> **Tip:** Regular `.json` files work with a simple `fetch()` or `requests.get()`. Use `.gz` files when bandwidth matters (mobile apps, frequent polling, etc).

---

## Web Pages

| Page | URL | Description |
|------|-----|-------------|
| Homepage | [connect-cdn.itzmrz.xyz](https://connect-cdn.itzmrz.xyz/) | Live stats, all endpoints, code examples |
| Open Labs | [/openlabs.html](https://connect-cdn.itzmrz.xyz/openlabs.html) | Lab availability viewer with NOW/UPCOMING/PASSED slots |
| Backups | [/backups.html](https://connect-cdn.itzmrz.xyz/backups.html) | Browse and download historical semester data |

---

## How It Works

1. **Daily cron** (GitHub Actions at 12:00 PM BDT / 6:00 AM UTC) runs `update_cdn.py`
2. Fetches fresh data from [usis-cdn.eniamza.com/connect.json](https://usis-cdn.eniamza.com/connect.json) with ETag caching
3. Generates all JSON files: `connect.json`, `exams.json`, `open_labs.json`, `latest.json`
4. Detects semester changes automatically (when mid exam dates change) and creates new backup files
5. Bumps version in `version.json` (MAJOR.SEMESTER.DAILY format)
6. Commits and pushes — GitHub Pages serves it instantly

### Backup naming

Backups use clean, human-readable filenames:
- `/backups/spring2026.json` — current semester (also available as `/latest.json`)
- `/backups/fall2025.json` — archived
- `/backups/summer2025.json` — archived

When a new semester starts (detected by changed mid-exam dates), the old backup is preserved and a new one is created.

---

## Run Locally

```bash
git clone https://github.com/itzMRZ/mrz-connect-cdn.git
cd mrz-connect-cdn
pip install requests
python update_cdn.py          # Fetch + generate all files
python update_cdn.py --force  # Skip ETag cache, force refresh
```

### Project Structure

```
├── connect.json              # Full course data (primary)
├── latest.json               # Current semester alias
├── exams.json                # Exam schedules only
├── open_labs.json            # Lab availability
├── connect_metadata.json     # Lightweight stats
├── connect_backup.json       # Backup index
├── version.json              # Version tracking (MAJOR.SEMESTER.DAILY)
├── backups/                  # Semester archives
│   ├── spring2026.json
│   ├── fall2025.json
│   └── ...
├── index.html                # Landing page
├── openlabs.html             # Lab availability viewer
├── backups.html              # Backup browser
├── 404.html                  # Redirect handler for old URLs
├── update_cdn.py             # Main update script
├── generate_backup_index.py  # Backup index generator
├── generate_free_labs.py     # Lab availability generator
└── .github/workflows/        # GitHub Actions (daily cron + yearly cleanup)
```

## Credits

Data source by [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com/connect.json)

## License

MIT
