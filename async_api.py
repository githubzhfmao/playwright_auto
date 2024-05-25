import asyncio
import pathlib
import auto
from playwright.async_api import async_playwright, Browser

from config import global_config

path_to_extension = "C:/Users/mecool/AppData/Local/Google/Chrome/User Data/Default" \
                    "/Extensions/dmkamcknogkgcdfhhbddcghachkejeap/0.12.90_0"

password = global_config.get('config', 'password').strip()
async def add_extension(playwright: async_playwright, index: int) -> Browser:
    user_data_dir = pathlib.Path(f"./profile/profile_{index}").absolute()
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=[
            # "--headless=new",
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],
    )

    if len(browser.background_pages) == 0:
        background_page = await browser.wait_for_event('backgroundpage')
    else:
        background_page = browser.background_pages[0]

    # Test the background page as you would any other page.
    return browser
async def main():
    async with async_playwright() as p:
        browser = await auto.add_extension(p, 3)
        # await browser.pages[0].goto("https://testnet.elys.network/")
        await auto.insert_wallet('half birth furnace napkin cool admit report cake surround midnight govern arch', password)
        # print(await page.title())
        # await page.screenshot(path="example.png")
        print(browser.pages)
        input(111)
        await browser.close()

asyncio.run(main())

# import os
# for i in range(1, 1001):
#     path = str(user_data_dir) + '/profile_' + str(i)
#     print(path)
#     os.mkdir(path)
