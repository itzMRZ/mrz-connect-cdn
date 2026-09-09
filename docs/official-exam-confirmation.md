# Official exam confirmation

`exam_status.json` controls the official PDF overlay used when generating `exams.json`. Confirmed matching records replace the CDN values and are marked with `source: "pdf"`; unmatched records remain `source: "cdn"`.

After manually parsing an official PDF in `exam-routine`, add a record under the normalized semester key:

```json
{
  "schemaVersion": 1,
  "semesters": {
    "summer2026": {
      "final": {
        "confirmed": true,
        "source": "official-pdf",
        "dataUrl": "https://bracu-exam-routine.itzmrz.xyz/exam_data.json",
        "updatedAt": "2026-07-22T18:49:21Z"
      }
    }
  }
}
```

Use `final` for a final routine. Leave an exam absent or set `confirmed` to `false` while it is still tentative in Connect.

For a `final` record, optionally add `midExamStartDate` / `midExamEndDate` (the official midterm window of that semester). `update_cdn.py` needs them to build correct phase metadata when it serves the record's payload as the active schedule.

The exam-routine site tries this endpoint only after loading its local data. If the endpoint or official URL fails, it keeps using the local file.

### Active-window serving (semester transitions)

`generate_exams_json()` normally derives the semester from the current USIS snapshot and merges confirmed records under that semester key only. When USIS publishes the next semester early (it does), confirmed records for the still-active semester would be ignored. To cover that window, the generator also scans **all** confirmed records and, if one's official exam window (payload dates) is active or imminent (grace: 14 days before start, 2 days after end) and its semester differs from the USIS semester, it serves that official payload as `exams.json` (all entries `source: "pdf"`). This keeps the site on the real exam period automatically and reverts to USIS data once the window ends — no manual flip of `exams.json` or `status.json` needed.
