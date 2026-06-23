import asyncio
from playwright.asyncio_api import async_playwright
import pandas as pd
import sys

async def scrape_cannes_tracker():
    async with async_playwright() as p:
        print("Launching headless cloud browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening tracker...")
        try:
            await page.goto("https://cannes26tracker.netlify.app/", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            sys.exit(1)
        
        print("Waiting for dynamic data to populate...")
        try:
            # Wait up to 20 seconds for the loading state text to disappear
            await page.wait_for_selector("text=Cargando tracker…", state="detached", timeout=20000)
            # Give it 2 extra seconds just to ensure the DOM fully renders
            await page.wait_for_timeout(2000)
        except Exception:
            print("Note: Loader element timeout or fast load. Proceeding to read content...")

        html_content = await page.content()
        body_text = await page.evaluate("() => document.body.innerText")
        
        print("\n--- Raw Data Preview ---")
        print(body_text[:1500])
        
        # Save raw HTML to help diagnose if pandas fails again
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        try:
            dfs = pd.read_html(html_content)
            if dfs:
                print(f"\nFound {len(dfs)} table(s)! Saving to 'cannes_2026_data.csv'...")
                dfs[0].to_csv("cannes_2026_data.csv", index=False)
                print("CSV file generated successfully.")
            else:
                print("\nNo HTML tables detected. Saving raw text content instead.")
                with open("cannes_2026_text.txt", "w", encoding="utf-8") as f:
                    f.write(body_text)
        except Exception as e:
            print(f"\nPandas read_html failed: {e}. Saving raw text content as a backup.")
            with open("cannes_2026_text.txt", "w", encoding="utf-8") as f:
                f.write(body_text)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_cannes_tracker())
