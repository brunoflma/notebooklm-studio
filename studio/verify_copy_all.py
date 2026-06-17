import os
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Grant clipboard permissions
        context = await browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
        page = await context.new_page()

        # Load the local HTML file
        abs_path = os.path.abspath('studio/notebooklm_studio.html')
        await page.goto(f'file://{abs_path}')

        # Inject mock data into the output div
        await page.evaluate("""() => {
            const out = document.getElementById('output');

            const block1 = document.createElement('div');
            block1.className = 'block';
            block1.innerHTML = '<span class="block-cmd">test-cmd-1</span><div class="block-out">test-out-1</div>';
            out.appendChild(block1);

            const block2 = document.createElement('div');
            block2.className = 'block';
            block2.innerHTML = '<span class="block-cmd">test-cmd-2</span><div class="block-err">test-err-2</div>';
            out.appendChild(block2);

            // Show the copy all button
            document.getElementById('copy-all-btn').style.display = 'block';
        }""")

        # Click the "Copy All" button
        await page.click('#copy-all-btn')

        # Wait a bit for the clipboard operation to complete
        await asyncio.sleep(0.5)

        # Verify the clipboard content
        clipboard_content = await page.evaluate("navigator.clipboard.readText()")

        expected_content = "test-cmd-1\ntest-out-1\n\ntest-cmd-2\ntest-err-2"
        print(f"Clipboard content: {repr(clipboard_content)}")
        print(f"Expected content:  {repr(expected_content)}")

        if clipboard_content == expected_content:
            print("Verification SUCCESSFUL")
        else:
            print("Verification FAILED")
            exit(1)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
