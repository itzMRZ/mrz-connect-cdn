## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-12 - Duplicate DOM Initialization
**Learning:** Found two separate script blocks initializing the same "Copy" buttons (one inline, one on DOMContentLoaded). This caused redundant DOM traversals and potential memory leaks with closure creation inside loops.
**Action:** Always audit existing event listeners and initialization scripts before adding new ones. Consolidate similar DOM manipulations into a single, optimized function running at the appropriate lifecycle event.
