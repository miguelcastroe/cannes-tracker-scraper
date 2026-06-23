import asyncio
from playwright.asyncio_api import async_playwright
import pandas as pd

async def scrape_cannes_tracker():
    async with async_playwright() as p:
        print("Launching headless cloud browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening tracker...")
        await page.goto("https://cannes26tracker.netlify.app/")
        
        print("Waiting for dynamic data to populate...")
        try:
            # Wait up to 20 seconds for the loading state text to disappear
            await page.wait_for_selector("text=Cargando tracker…", state="detached", timeout=20000)
        except Exception:
            print("Note: Loader element timeout or fast load. Proceeding to read content...")

        html_content = await page.content()
        body_text = await page.evaluate("() => document.body.innerText")
        
        print("\n--- Raw Data Preview ---")
        print(body_text[:1000])
        
        try:
            dfs = pd.read_html(html_content)
            if dfs:
                print(f"\nFound {len(dfs)} table(s)! Saving to 'cannes_2026_data.csv'...")
                dfs[0].to_csv("cannes_2026_data.csv", index=False)
                print("CSV file generated successfully.")
            else:
                print("\nNo HTML tables detected. Data might be formatted in a custom UI grid.")
        except ValueError:
            print("\nCould not parse table structures from the raw HTML.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_cannes_tracker())
