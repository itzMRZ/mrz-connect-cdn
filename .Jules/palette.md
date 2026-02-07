## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2025-10-26 - [Code Consolidation & API DX]
**Learning:** Initializing UI elements (like copy buttons) in multiple places leads to duplicate controls and bugs. Consolidating initialization logic into a single reusable function prevents this and makes it easy to extend functionality to new elements (like API endpoints).
**Action:** Always check for existing initialization loops before adding new ones. Refactor into reusable functions when targeting multiple element types.
