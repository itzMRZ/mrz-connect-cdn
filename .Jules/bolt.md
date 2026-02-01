## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-12 - Frontend Redundancy
**Learning:** Legacy code often accumulates duplicate logic (e.g., multiple copy-to-clipboard implementations) which can lead to UI bugs (duplicate buttons) and performance waste (redundant event listeners).
**Action:** Always audit `index.html` or main entry points for duplicate event listeners or initialization blocks, especially when working with vanilla JS. Consolidate helper functions outside of loops.
