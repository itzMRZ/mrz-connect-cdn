## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-20 - Duplicate Initialization Anti-Pattern
**Learning:** `index.html` contained duplicate logic for copy buttons (one inline, one in `DOMContentLoaded`), causing double execution and redundant DOM nodes.
**Action:** Always `grep` for existing feature implementations in single-page HTML files before adding new logic to prevent duplication and layout thrashing.
