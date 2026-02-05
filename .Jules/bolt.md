## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-12 - Duplicate DOM Initialization
**Learning:** Avoid running initialization logic both inline and in 'DOMContentLoaded'. This can lead to duplicate UI elements (like multiple copy buttons) and wasted memory.
**Action:** Use a single entry point (preferably 'DOMContentLoaded' or 'defer') for UI initialization. Hoist helper functions out of loops to reduce memory allocation.
