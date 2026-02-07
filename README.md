# MRZ Connect CDN

[![VibeCoded](https://img.shields.io/badge/VibeCoded-2E2E2E?style=flat-square&logo=githubcopilot&logoColor=auto&labelColor=8000FF)](http://vibe-coding.urbanup.com/18529533)
[![MIT License](https://img.shields.io/badge/License-MIT-56d364?style=flat-square)](https://github.com/itzMRZ/mrz-connect-cdn/blob/main/LICENSE)
[![Website](https://img.shields.io/badge/Website-Live-58a6ff?style=flat-square)](https://connect-cdn.itzmrz.xyz/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/itzMRZ/mrz-connect-cdn)

Open-source JSON API serving BRAC University course data, exam schedules, and lab availability. Automatically updated daily via GitHub Actions and hosted on GitHub Pages.

**Website:** https://connect-cdn.itzmrz.xyz

---

## Quick Start

```js
// Get the latest data (whatever USIS currently has)
const data = await fetch('https://connect-cdn.itzmrz.xyz/connect.json').then(r => r.json());

// Get stable current semester data (won't switch until finals end)
const stable = await fetch('https://connect-cdn.itzmrz.xyz/stable.json').then(r => r.json());
```

```python
import requests

# Latest data
data = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()

# Stable current semester
stable = requests.get('https://connect-cdn.itzmrz.xyz/stable.json').json()
```

---

## connect.json vs stable.json

This is the key design decision of the CDN.

**Problem:** USIS sometimes publishes next semester's data mid-current-semester. If you're building a tool for the current semester (exam prep, seat tracker, etc.), you don't want your data to suddenly switch to next semester while you're still in the middle of finals.

**Solution:**

| File | Behavior | Use when |
|------|----------|----------|
| `connect.json` | Always the latest data from USIS. If USIS publishes next semester data mid-current, connect.json switches immediately. | You want the freshest data available, or you're building next-semester planning tools. |
| `stable.json` | Locked to the current semester. Only switches after the **final exam end date** passes. Daily seat/schedule updates still apply within the same semester. | You need reliable current-semester data — exam prep apps, seat availability trackers, anything that shouldn't break mid-semester. |

**Example timeline:**
```
March 2026:  connect.json = Spring 2026    stable.json = Spring 2026    (same)
April 2026:  USIS publishes Summer 2026 data early
             connect.json = Summer 2026    stable.json = Spring 2026    (different!)
May 21 2026: Spring 2026 finals end
May 22 2026: connect.json = Summer 2026    stable.json = Summer 2026    (synced again)
```

Both files have identical structure. Just pick the one that fits your use case.

---

## All API Endpoints

| Endpoint | Description | Size |
|----------|-------------|------|
| [`/connect.json`](https://connect-cdn.itzmrz.xyz/connect.json) | Latest API data — always whatever USIS currently has | ~3.4 MB |
| [`/stable.json`](https://connect-cdn.itzmrz.xyz/stable.json) | Current semester, locked until finals end | ~3.4 MB |
| [`/exams.json`](https://connect-cdn.itzmrz.xyz/exams.json) | Exam schedules only (mid + final dates/times) | ~516 KB |
| [`/open_labs.json`](https://connect-cdn.itzmrz.xyz/open_labs.json) | Lab room availability by day and time slot | ~387 KB |
| [`/connect_metadata.json`](https://connect-cdn.itzmrz.xyz/connect_metadata.json) | Lightweight stats only (section count, seats, exam ranges) | ~400 B |
| [`/connect_backup.json`](https://connect-cdn.itzmrz.xyz/connect_backup.json) | Index of all semester backups with CDN links | ~2 KB |
| [`/backups/{season}{year}.json`](https://connect-cdn.itzmrz.xyz/backups/spring2026.json) | Individual semester archives | ~3.4 MB |

Every JSON file also has a `.gz` variant (append `.gz` to the URL) for ~96% smaller downloads.

### Which file should I use?

- **Building a course tool / seat tracker?** → `/stable.json` (won't break mid-semester)
- **Planning next semester?** → `/connect.json` (always latest, could be next semester already)
- **Only need exams?** → `/exams.json` (much lighter)
- **Finding open labs?** → `/open_labs.json`
- **Just need stats / section count?** → `/connect_metadata.json` (~400 bytes vs 3.4 MB)
- **Want historical data?** → `/connect_backup.json` to discover semesters, then `/backups/{season}{year}.json`

---

## Data Structure

### connect.json / stable.json

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
    "stableUrl": "https://connect-cdn.itzmrz.xyz/stable.json",
    "currentBackups": 1,
    "archivedBackups": 5,
    "cdnBaseUrl": "https://connect-cdn.itzmrz.xyz/backups"
  },
  "backups": [
    {
      "semester": "Spring2026",
      "totalSections": 2353,
      "cdnLink": "https://connect-cdn.itzmrz.xyz/backups/spring2026.json",
      "isCurrent": true,
      "filename": "spring2026.json"
    }
  ]
}
```

---

## Gzip Compression

Every JSON file has a `.gz` version for much smaller downloads:

| File | Regular | Gzipped | Savings |
|------|---------|---------|---------|
| connect.json | ~3.4 MB | ~137 KB | 96% |
| stable.json | ~3.4 MB | ~137 KB | 96% |
| exams.json | ~516 KB | ~20 KB | 96% |
| open_labs.json | ~387 KB | ~15 KB | 96% |

**JavaScript (gzipped):**
```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json.gz')
  .then(r => r.blob())
  .then(blob => blob.stream().pipeThrough(new DecompressionStream('gzip')))
  .then(stream => new Response(stream).json())
  .then(data => console.log(data.metadata));
```

**Python (gzipped):**
```python
import requests, gzip, json
r = requests.get('https://connect-cdn.itzmrz.xyz/connect.json.gz')
data = json.loads(gzip.decompress(r.content))
```

> **Tip:** Regular `.json` files work with a simple `fetch()` or `requests.get()`. Use `.gz` when bandwidth matters (mobile apps, frequent polling).

---

## Web Pages

| Page | URL | Description |
|------|-----|-------------|
| Homepage | [connect-cdn.itzmrz.xyz](https://connect-cdn.itzmrz.xyz/) | Live stats, all endpoints, code examples |
| Open Labs | [/openlabs.html](https://connect-cdn.itzmrz.xyz/openlabs.html) | Lab availability with NOW/UPCOMING/PASSED time slots |
| Backups | [/backups.html](https://connect-cdn.itzmrz.xyz/backups.html) | Browse and download historical semester data |

---

## How It Works

1. **Daily cron** (GitHub Actions, 12:00 PM BDT / 6:00 AM UTC) runs `update_cdn.py`
2. Fetches fresh data from [usis-cdn.eniamza.com/connect.json](https://usis-cdn.eniamza.com/connect.json) (with ETag caching)
3. Writes `connect.json` — always the raw latest from the API
4. Updates `stable.json` — only if same semester, or previous semester's finals have ended
5. Generates `exams.json`, `open_labs.json`, backup index
6. Detects semester changes (when mid-exam dates differ) and creates new backup files
7. Bumps version in `version.json` (MAJOR.SEMESTER.DAILY)
8. Commits and pushes — GitHub Pages serves immediately

### Semester end detection

`stable.json` detects semester end by checking the `finalExamEndDate` field in its own metadata. If today's date is past that date and the API has different semester data, stable.json switches. Otherwise, it stays frozen on the current semester's data.

### Backup naming

Clean, human-readable filenames:
- `/backups/spring2026.json`, `/backups/fall2025.json`, `/backups/summer2024.json`
- When a new semester starts, the old backup is preserved and a new one is created

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
├── connect.json              # Latest API data (always freshest)
├── stable.json               # Current semester (frozen until finals end)
├── exams.json                # Exam schedules only
├── open_labs.json            # Lab availability
├── connect_metadata.json     # Lightweight stats
├── connect_backup.json       # Backup index
├── version.json              # Version (MAJOR.SEMESTER.DAILY)
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
└── .github/workflows/        # Daily cron + yearly cleanup
```

## Credits

Data source by [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com/connect.json)

## License

MIT
