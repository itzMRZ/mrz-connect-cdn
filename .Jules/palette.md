## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2024-05-22 - [Modal Accessibility]
**Learning:** Modals often trap keyboard users if the close button is not focusable (like a span). Always use a `<button>` for close actions and manage focus (save/restore) to maintain context.
**Action:** Check all modals for `role="dialog"`, focusable close buttons, and focus management.
