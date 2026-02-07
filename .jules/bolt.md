## 2025-10-26 - [Duplicate Event Initialization in Static HTML]
**Learning:** Found critical anti-pattern where the same UI feature (copy buttons) was initialized twice: once inline and once on `DOMContentLoaded`. This resulted in duplicate DOM elements and redundant event listeners.
**Action:** When working with vanilla JS in static HTML files, always audit the entire file for multiple script blocks modifying the same DOM elements before implementing changes. Use event delegation to decouple initialization from event handling.
