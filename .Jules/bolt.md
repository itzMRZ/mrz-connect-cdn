## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-10-24 - Duplicate DOM Initialization
**Learning:** Found duplicate initialization logic for UI components (copy buttons) in `index.html`. One block used legacy/slow methods (`innerText`), the other used modern/fast methods (`textContent`), running simultaneously.
**Action:** When auditing `index.html` or legacy scripts, always check for redundant event listeners or initialization blocks that might have been "overwritten" by newer code but not actually removed.
