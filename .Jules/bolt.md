## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-05-24 - Duplicate Event Listeners & Reflow
**Learning:** Duplicate event listeners (one inline, one on DOMContentLoaded) targeting the same or nested elements can silently waste memory and cause UI glitches (double buttons). Also, `innerText` triggers a reflow (layout calculation) while `textContent` does not.
**Action:** Always check for existing initialization logic when adding "feature" scripts. Use `textContent` for reading code blocks where visual styling doesn't matter for the copied text.
