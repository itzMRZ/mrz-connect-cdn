
from playwright.sync_api import sync_playwright, expect
import time

def verify_copy(page):
    print("Navigating...")
    page.goto("http://localhost:8080/index.html")

    # Wait for containers
    container = page.locator('.code-container').first
    expect(container).to_be_visible()

    # Check button existence
    btn = container.locator('.copy-btn')
    expect(btn).to_be_attached()

    # Verify only one button
    count = container.locator('.copy-btn').count()
    print(f"Buttons found in first container: {count}")
    if count != 1:
        raise Exception(f"Expected 1 button, found {count}")

    # Force button to be visible (opacity 1) for screenshot
    # Note: The CSS uses .code-container:hover .copy-btn { opacity: 1 }
    # We can simulate hover or force style.
    btn.evaluate("el => el.style.opacity = '1'")

    # Click button
    print("Clicking button...")
    btn.click()

    # Check text change
    expect(btn).to_have_text("Copied!")
    print("Text changed to 'Copied!'")

    # Screenshot
    page.screenshot(path="verification/copy_verified.png")
    print("Screenshot saved.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        try:
            verify_copy(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
