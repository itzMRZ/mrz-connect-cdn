# Official exam confirmation

`exam_status.json` controls the official PDF overlay used when generating `exams.json`. Confirmed matching records replace the CDN values and are marked with `source: "pdf"`; unmatched records remain `source: "cdn"`.

After manually parsing an official PDF in `exam-routine`, add a record under the normalized semester key:

```json
{
  "schemaVersion": 1,
  "semesters": {
    "summer2026": {
      "midterm": {
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

The exam-routine site tries this endpoint only after loading its local data. If the endpoint or official URL fails, it keeps using the local file.
