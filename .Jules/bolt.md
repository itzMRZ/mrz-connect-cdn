## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-31 - DOM Performance: Reflows & Duplicate Logic
**Learning:** Duplicate event listeners or initialization blocks (one inline, one on DOMContentLoaded) can silently accumulate, causing double execution. Also, accessing `innerText` forces a layout reflow (style calculation), while `textContent` does not.
**Action:** Always audit `index.html` for scattered script tags. Consolidate logic into a single `DOMContentLoaded` listener. Prefer `textContent` for reading hidden or code-block text.
