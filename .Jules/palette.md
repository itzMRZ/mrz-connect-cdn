## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2025-10-26 - [Ghost Controls]
**Learning:** Split initialization logic (inline + DOMContentLoaded) for the same UI components caused duplicate 'Copy' buttons, potentially confusing screen reader users.
**Action:** Centralize component initialization in a single idempotent function or lifecycle event.
