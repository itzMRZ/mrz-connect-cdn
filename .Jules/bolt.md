## 2026-01-12 - Conditional GET Optimization
**Learning:** The `requests` library in Python makes it very easy to handle ETags manually. Storing the ETag in a simple text file (`connect.etag`) is a sufficient and lightweight persistence mechanism for this use case.
**Action:** When working with scripts that periodically fetch data, always check if the upstream server supports ETags or Last-Modified to avoid redundant downloads.

## 2026-01-25 - Duplicate Event Listeners in Vanilla JS
**Learning:** In a single HTML file architecture, script blocks can easily accumulate over time, leading to duplicate initialization logic (e.g., adding multiple identical event listeners or UI elements). Specifically, one block ran immediately while another waited for `DOMContentLoaded`, causing double rendering of copy buttons.
**Action:** When refactoring vanilla JS in HTML files, always audit the entire file for redundant script blocks, especially when mixing inline execution with event-driven execution.
