## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-05-22 - Duplicate Event Listeners in Static HTML
**Learning:** In static HTML pages with inline scripts, it's easy to accidentally initialize UI components (like copy buttons) twice—once in an inline script and once in a DOMContentLoaded listener.
**Action:** Always check for existing event listeners or components before initializing, or consolidate initialization logic into a single DOMContentLoaded block.
