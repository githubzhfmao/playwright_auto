from playwright.async_api import async_playwright

import auto
import asyncio
import swap
import wallet
from config import global_config
from loguru import logger

password = global_config.get('config', 'password').strip()
worktype = global_config.get('config', 'worktype').strip()

async def insert_wallet_main(index: int, seed: str):
    async with async_playwright() as p:
        browser = await auto.add_extension(p, index)
        # await browser.pages[0].goto("https://testnet.elys.network/")
        await auto.insert_wallet(seed, password)
        # print(await page.title())
        # await page.screenshot(path="example.png")
        await browser.close()


def run_insert_wallet():
    wallet_path = global_config.get('path', 'wallet_path').strip()
    seed_phrases = wallet.get_mnemonic(wallet_path)
    result_path = global_config.get('path', 'result_path').strip()
    result = open(str(result_path) + 'result.txt', mode='a', encoding='utf-8')
    for i in range(1, len(seed_phrases)):
        seed_phrase = seed_phrases[i]
        asyncio.run(insert_wallet_main(i, seed_phrase))

def run_swap():
    wallet_path = global_config.get('path', 'wallet_path').strip()
    seed_phrases = wallet.get_mnemonic(wallet_path)
    result_path = global_config.get('path', 'result_path').strip()
    result = open(str(result_path) + 'result.txt', mode='a', encoding='utf-8')
    for i in range(1, len(seed_phrases)):
        try:
            asyncio.run(swap.swap(i))
        except Exception as e:
            print(e)
            result.write(f' {i} ' + str(e))

if __name__ == '__main__':
    if worktype == 'insert_wallet':
        run_insert_wallet()
    if '1'  in worktype:
        run_swap()
