## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2026-01-28 - [Unified Interactive Components]
**Learning:** Reusing interaction logic (like copy buttons) across different UI elements (code blocks vs. endpoints) requires consistent CSS context (positioning, hover states) to ensure predictable behavior.
**Action:** When extending a UI pattern to a new element type, verify that the new container supports the necessary CSS states (e.g., `position: relative` for absolute children, `:hover` for visibility).
