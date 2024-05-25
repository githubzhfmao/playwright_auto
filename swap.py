import asyncio
import pathlib
import random
import re
import auto
from playwright.async_api import async_playwright, Browser
from loguru import logger


async def swap(index: int):
    logger.info(f"Starting swap {index}")
    async with async_playwright() as p:
        browser = await auto.add_extension(p, index)
        page = browser.pages[0]
        await page.goto("https://testnet.elys.network/")
        # await auto.start()
        await page.wait_for_load_state("networkidle")
        await auto.start()

        await page.reload()
        await page.wait_for_load_state("networkidle")
        signin = await auto.role_click(page, "link", name="Sign In", retry=1)

        if signin:
            await auto.role_click(page, "button", name="Connect with Wallet")
            await auto.role_click(page, "button", name="Keplr")
            await auto.confirm()
            await page.reload()
            await page.wait_for_load_state("networkidle")

            signin = await auto.role_click(page, "link", name="Sign In", retry=1)
            if signin:
                await auto.role_click(page, "button", name="Connect with Wallet")
                await auto.role_click(page, "button", name="Keplr")
                await auto.confirm()
                await page.reload()
                await page.wait_for_load_state("networkidle")

        coins = ['USDC', 'ATOM', "TIA"]
        await swap_task(coins[random.randint(0, 2)], page)
        await staking_task(page)
        await lp_task(page)
        await browser.close()

async  def lp_task(page):
    logger.info("Starting lp")
    await page.goto("https://testnet.elys.network/earn/mining")
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await page.locator("div").filter(has_text=re.compile(r"^Add Liquidity$")).first.click()
    await page.get_by_placeholder("0.0").first.fill(
        '%.4f' % (random.uniform(0.001, 0.01)))

    await page.wait_for_timeout(6000)
    await page.get_by_role("group").get_by_role("button", name="Deposit").click()
    await auto.confirm(False)

    await page.wait_for_timeout(6000)

async  def staking_task(page):
    logger.info("Starting staking")
    await page.goto("https://testnet.elys.network/earn/staking")
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await page.get_by_role("button", name="Manage").nth(1).click()
    await page.get_by_placeholder("0.0").first.fill(
        '%.4f' % (random.uniform(0.001, 0.01)))

    await page.wait_for_timeout(6000)
    btn_flg = await auto.role_click(page, "button", name="Stake ELYS")
    if btn_flg:
        await auto.confirm()

async def swap_task(coin, page):
    await page.goto(f"https://testnet.elys.network/swap#ELYS/{coin}")
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await page.get_by_placeholder("0.0").first.click()
    await page.get_by_placeholder("0.0").first.fill(
        '%.4f' % (random.uniform(0.001, 0.01)))
    await page.wait_for_timeout(6000)
    btn_flg = await auto.role_click(page, "button", name=f"Receive {coin}")
    if btn_flg:
        await auto.confirm()
# asyncio.run(swap(2))

# import os
# for i in range(1, 1001):
#     path = str(user_data_dir) + '/profile_' + str(i)
#     print(path)
#     os.mkdir(path)
