## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-05-21 - Consolidating DOM Initialization
**Learning:** Duplicate script execution (inline vs DOMContentLoaded) can lead to redundant UI elements and event listeners. Centralizing initialization logic is crucial for single-page apps or static sites with dynamic behaviors.
**Action:** Audit `index.html` or template files for duplicate script tags or logic that might run multiple times on the same elements.
