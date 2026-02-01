## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-05-22 - Duplicate Inline Scripts
**Learning:** Inline scripts that run immediately and `DOMContentLoaded` listeners can inadvertently duplicate logic if they target similar elements (e.g., `.code-container` vs `.code-block`).
**Action:** Always consolidate initialization logic into a single lifecycle hook (like `DOMContentLoaded`) and verify element counts to catch duplicate instantiations.
