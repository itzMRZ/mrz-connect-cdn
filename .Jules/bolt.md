## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-12 - DOM Performance & Selectors
**Learning:** `innerText` triggers a reflow, while `textContent` does not. For static content like code blocks, `textContent` is always preferred. Also, always check for duplicate event listeners or DOM insertions when working with both inline scripts and `DOMContentLoaded`.
**Action:** When initializing UI components (like copy buttons), ensure the initialization logic is idempotent (checks if component exists) and centralized. Use `textContent` for reading text.
