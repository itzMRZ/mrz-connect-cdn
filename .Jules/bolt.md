## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-13 - Duplicate DOM Initialization
**Learning:** Inline scripts combined with `DOMContentLoaded` listeners can lead to duplicate UI initialization if not carefully managed. In this case, copy buttons were added twice: once immediately to containers, and once on load to blocks.
**Action:** Centralize UI initialization in a single `DOMContentLoaded` listener and verify that elements don't already exist before appending.
