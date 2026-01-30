## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-13 - Duplicate Event Listeners
**Learning:** Mixing inline scripts and `DOMContentLoaded` listeners can lead to duplicate functionality (e.g., two copy buttons per code block) if not carefully managed.
**Action:** Consolidate initialization logic into a single lifecycle hook and verify the count of generated UI elements during testing.
