## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2025-10-26 - [Initialization Consolidation]
**Learning:** Duplicate copy buttons appeared because initialization logic was split between inline scripts and DOMContentLoaded.
**Action:** Always consolidate component initialization into a single, scoped function that handles all instances (e.g., `setupCopyButton`).

## 2025-10-26 - [Fallback Copy Scroll]
**Learning:** The fallback `document.execCommand('copy')` technique using a hidden textarea can cause the page to scroll to the bottom if `top: 0` is not set along with `position: fixed`.
**Action:** Always ensure hidden interaction elements have `top: 0` to prevent viewport jumps on focus.
