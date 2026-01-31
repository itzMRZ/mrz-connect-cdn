## 2024-05-22 - [Copy to Clipboard]
**Learning:** Developers frequently need to copy-paste code snippets from documentation. Adding a dedicated "Copy" button reduces friction and improves the developer experience significantly.
**Action:** When designing documentation pages, always include a "Copy" button for code blocks.

## 2025-10-18 - [Touch Accessibility for Hover Controls]
**Learning:** Hiding controls with `opacity: 0` and showing them only on `:hover` makes them inaccessible on touch devices where hover is not a standard state.
**Action:** Use `@media (hover: hover)` to wrap the opacity logic, ensuring controls remain visible by default on touch devices.
