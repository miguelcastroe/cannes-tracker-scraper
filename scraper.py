import asyncio
from playwright.asyncio_api import async_playwright
import pandas as pd
import sys

async def scrape_cannes_tracker():
    async with async_playwright() as p:
        print("Launching headless cloud browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://cannes26tracker.netlify.app/"
        print(f"Opening tracker at {url}...")
        try:
            await page.goto(url, timeout=60000)
        except Exception as e:
            print(f"ERROR: Failed to load page: {e}")
            await browser.close()
            sys.exit(1)
        
        print("Waiting for dynamic data to populate...")
        try:
            # Wait for loader element to vanish
            await page.wait_for_selector("text=Cargando tracker…", state="detached", timeout=20000)
            await page.wait_for_timeout(3000)  # Safe buffer for table rendering
        except Exception as e:
            print(f"Note on wait selector: {e}. Proceeding anyway...")

        html_content = await page.content()
        body_text = await page.evaluate("() => document.body.innerText")
        
        print("\n--- Raw Data Preview ---")
        print(body_text[:1500])
        
        # Save raw assets for download backup
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        with open("cannes_2026_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        # Attempt to parse HTML tables
        try:
            dfs = pd.read_html(html_content, flavor='html5lib')
            if dfs:
                print(f"\nSuccess! Found {len(dfs)} table(s). Saving data to CSV...")
                dfs[0].to_csv("cannes_2026_data.csv", index=False)
                print("CSV file generated.")
            else:
                print("\nNo standard <table> elements detected. Content likely utilizes a div/grid structure.")
        except Exception as e:
            print(f"\nPandas parsing bypassed or failed: {e}.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_cannes_tracker())
