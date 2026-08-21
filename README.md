# MRZ Connect CDN

[![VibeCoded](https://img.shields.io/badge/VibeCoded-2E2E2E?style=flat-square&logo=githubcopilot&logoColor=auto&labelColor=8000FF)](http://vibe-coding.urbanup.com/18529533)
[![MIT License](https://img.shields.io/badge/License-MIT-56d364?style=flat-square)](https://github.com/itzMRZ/mrz-connect-cdn/blob/main/LICENSE)
[![Website](https://img.shields.io/badge/Website-Live-58a6ff?style=flat-square)](https://connect-cdn.itzmrz.xyz/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/itzMRZ/mrz-connect-cdn)

Open-source JSON API for BRAC University course data, exams, and lab availability. Updates daily via GitHub Actions.

Website: [connect-cdn.itzmrz.xyz](https://connect-cdn.itzmrz.xyz)

## Contents

- Quick Start
- Choose: `connect.json` vs `stable.json`
- API endpoints
- Response shapes (what fields exist)
- Gzip downloads (`.gz`)
- Web pages
- How updates + stability work
- Run locally

## Quick Start

```js
// Latest data (whatever USIS currently publishes)
const latest = await fetch('https://connect-cdn.itzmrz.xyz/connect.json').then(r => r.json());

// Stable current-semester data (won’t switch until finals end)
const stable = await fetch('https://connect-cdn.itzmrz.xyz/stable.json').then(r => r.json());

console.log(latest.metadata.version, latest.metadata.totalSections);
```

```python
import requests

latest = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()
stable = requests.get('https://connect-cdn.itzmrz.xyz/stable.json').json()

print(stable['metadata']['version'], stable['metadata']['totalSections'])
```

## Choose: connect.json vs stable.json

USIS sometimes publishes next semester early (while the current semester is still ongoing). That’s why there are two “full data” files.

| File | What it guarantees | Best for |
| ---- | ------------------- | -------- |
| `connect.json` | **Always latest** (can switch to next semester mid-current) | Next-semester planning, “show me whatever USIS has right now” |
| `stable.json` | **Stays on current semester** until `finalExamEndDate` passes | Seat trackers, exam tools, anything that must not flip mid-semester |

Rule of thumb:

- If you want the newest semester as soon as it appears → use `connect.json`
- If you want the current semester until finals are actually over → use `stable.json`

## API endpoints

| Endpoint | What it is | Typical use |
| -------- | ---------- | ----------- |
| <https://connect-cdn.itzmrz.xyz/connect.json> | Full data, always latest | Next-semester planning |
| <https://connect-cdn.itzmrz.xyz/stable.json> | Full data, locked to current semester until finals end | Current-semester tools |
| <https://connect-cdn.itzmrz.xyz/exams.json> | Exams only | Timetables/calendars |
| <https://connect-cdn.itzmrz.xyz/open_labs.json> | Lab availability | Open lab finder |
| <https://connect-cdn.itzmrz.xyz/connect_metadata.json> | Metadata only (tiny) | Homepage stats, quick checks |
| <https://connect-cdn.itzmrz.xyz/connect_backup.json> | Index of semester backups | Discover history |
| <https://connect-cdn.itzmrz.xyz/backups/spring2026.json> | One semester snapshot | Historical compare |

Every JSON file also has a `.gz` variant (append `.gz`), typically ~96% smaller.

## Response shapes

This section is intentionally short: it shows the important top-level keys and the common fields you’ll use.

### connect.json / stable.json

```json
{
  "metadata": {
    "version": "2.3.1",
    "lastUpdated": "2026-02-07T06:00:00.000Z",
    "midExamStartDate": "2026-03-07",
    "finalExamEndDate": "2026-07-16",
    "totalSections": 2353
  },
  "sections": [
    {
      "courseCode": "CSE110",
      "sectionName": "01",
      "facultyName": "...",
      "totalSeat": 40,
      "consumedSeat": 35,
      "emptySeat": 5,
      "classDay": "ST",
      "classTime": "08:00 AM-09:20 AM",
      "classRoom": "...",
      "midExamDate": "YYYY-MM-DD",
      "finalExamDate": "YYYY-MM-DD"
    }
  ]
}
```

### exams.json

```json
{
  "metadata": {
    "totalExams": 2353,
    "midExamStartDate": "YYYY-MM-DD",
    "finalExamEndDate": "YYYY-MM-DD"
  },
  "exams": [
    {
      "courseCode": "CSE110",
      "sectionName": "01",
      "midExamDate": "YYYY-MM-DD",
      "finalExamDate": "YYYY-MM-DD"
    }
  ]
}
```

### connect_backup.json

```json
{
  "metadata": {
    "totalBackups": 6,
    "currentSemester": "Spring2026",
    "stableUrl": "https://connect-cdn.itzmrz.xyz/stable.json",
    "cdnBaseUrl": "https://connect-cdn.itzmrz.xyz/backups"
  },
  "backups": [
    {
      "semester": "Spring2026",
      "totalSections": 2353,
      "backupTime": "...",
      "cdnLink": "https://connect-cdn.itzmrz.xyz/backups/spring2026.json",
      "isCurrent": true,
      "filename": "spring2026.json"
    }
  ]
}
```

## Gzip downloads (`.gz`)

Use `.gz` when bandwidth matters.

Python:

```python
import requests, gzip, json
r = requests.get('https://connect-cdn.itzmrz.xyz/connect.json.gz')
data = json.loads(gzip.decompress(r.content))
```

JavaScript (browser):

```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json.gz')
  .then(r => r.blob())
  .then(b => b.stream().pipeThrough(new DecompressionStream('gzip')))
  .then(s => new Response(s).json())
  .then(data => console.log(data.metadata));
```

## Web pages

- [Homepage](https://connect-cdn.itzmrz.xyz/)
- [Open labs](https://connect-cdn.itzmrz.xyz/openlabs.html)
- [Backups browser](https://connect-cdn.itzmrz.xyz/backups.html)

## How updates + stability work

- Daily job runs at 12:00 PM BDT (6:00 AM UTC).
- `connect.json` is written from the latest USIS snapshot.
- `stable.json` updates daily within the same semester, but it **won’t switch semesters** until `finalExamEndDate` is in the past.
- Backups are created per semester inside `backups/` with clean names like `spring2026.json`.

## Run locally

```bash
git clone https://github.com/itzMRZ/mrz-connect-cdn.git
cd mrz-connect-cdn
pip install requests
python update_cdn.py
python update_cdn.py --force
```

## Credits

Data source by [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com/connect.json](https://usis-cdn.eniamza.com/connect.json)

## License

MIT
