## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-14 - Duplicate DOM Initialization
**Learning:** Found two independent blocks of JavaScript in `index.html` both initializing "Copy" buttons for the same elements. This caused duplicate buttons (visual clutter) and redundant event listeners (memory waste). One used `innerText` (reflow) and the other `textContent`.
**Action:** When working in a single HTML file with scattered scripts, always grep for similar selectors (e.g., `.code-container`) to ensure logic isn't being duplicated.
