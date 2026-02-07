## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2025-10-27 - [Refactoring Side Effects]
**Learning:** When removing 'duplicate' CSS blocks, critical properties (like `position: relative`) can be lost if they only existed in the 'duplicate' version. This can break absolute positioning of child elements.
**Action:** Always diff duplicate blocks carefully before consolidating to ensure no unique properties are lost.
