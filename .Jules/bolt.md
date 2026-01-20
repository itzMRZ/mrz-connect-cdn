## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-13 - DOM Reflow & Duplicate Logic
**Learning:** Extracting text using `innerText` forces the browser to calculate layout (reflow), which is expensive. Additionally, relying on both immediate script execution and `DOMContentLoaded` for the same elements can lead to duplicate UI components (like double copy buttons) if not carefully managed.
**Action:** Prefer `textContent` for reading text when visual styling isn't critical. Consolidate initialization logic into a single, idempotent function to prevent duplication and improve maintainability.
