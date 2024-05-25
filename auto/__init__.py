import pyautogui
import pathlib
from typing import (
    Pattern,
    Union,
)


import pygetwindow
from loguru import logger
from playwright.async_api import async_playwright, Browser, expect
from config import global_config
from playwright._impl._page import Page

extension_id = global_config.get('config', 'extension_id')
async def add_extension(playwright: async_playwright, index: int) -> Browser:
    path_to_extension = global_config.get('path', 'driver_path').strip()
    user_data_dir = pathlib.Path(f"./profile/profile_{index}").absolute()
    global browser
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=[
            # "--headless=new",
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],
    )
    return browser


async def get_wallet_page(wallet_name='Keplr'):
    idx: int = 0
    while True:
        nwp = await has_title(wallet_name)
        if nwp is not None or idx > 30:
            break
        else:
            logger.info(f"等待插件{wallet_name}...............{idx}")
            await browser.pages[0].wait_for_timeout(1000)
        idx += 1
    return nwp


async def has_title(title):
    for p in browser.pages:
        if p.title() == title:
            return p
    return None


async def locator_wait_for(page, selector, retry=3):
    locator = page.locator(selector)
    retry_cnt = 0
    while locator is None and retry_cnt < retry:
        await page.wait_for_timeout(1000)
        locator = page.locator(selector)
        retry_cnt += 1
    logger.info(f"等待元素{selector}")
    lc = await locator.count()
    for i in range(lc):
        await expect(locator.nth(i)).to_be_visible()
    return locator


async def insert_wallet(phrase, password):
    idx: int = 0
    while True:
        if len(browser.pages) > 1:
            break
        elif idx > 3:
            np = await browser.new_page()
            await np.goto(f'chrome-extension://{extension_id}/register.html#')
            break
        else:
            logger.info(f"等待插件...............{idx}")
            await browser.pages[0].wait_for_timeout(1000)
        idx += 1
    wp = browser.pages[1]
    await element_click(wp, '//button[div[text()="导入已有钱包"]]')
    await element_click(wp, '//button[div[text()="使用助记词或私钥"]]')
    phrases = phrase.split(" ")
    if len(phrases) == 24:
        await element_click(wp, '//button[text()="24个词"]')
        passwords = await locator_wait_for(wp, '//input[@type="password"]')
        for i in range(len(phrases)):
            await passwords.nth(i).fill(phrases[i])
            await element_click(wp, '//button[text()="24个词"]')
    elif len(phrases) == 1:
        await element_click(wp, '//button[text()="私钥"]')
    elif len(phrases) != 12:
        raise ValueError(f'助记词长度异常：{len(phrases)}')
    else:
        passwords = await locator_wait_for(wp, '//input[@type="password"]')
        for i in range(len(phrases)):
            await passwords.nth(i).fill(phrases[i])
            await element_click(wp, '//button[text()="12个词"]')

    await element_click(wp, '//button[div[text()="导入"]]')
    await wp.get_by_placeholder('例如：交易、NFT保险柜、投资').fill("AA")

    passwords2 = await locator_wait_for(wp, '//input[@type="password"]')
    pc2 = await passwords2.count()
    for i in range(pc2):
        await passwords2.nth(i).fill(password)
    await element_click(wp, '//button[div[text()="下一步"]]')
    await element_click(wp, '//button[div[text()="保存"]]')
    await element_click(wp, '//button[div[text()="完成"]]')
    # await add_keplr_chain()


async def add_keplr_chain(chain_name='Elys Network Testnet'):
    np = await browser.new_page()
    await np.goto('https://chains.keplr.app/')
    await np.get_by_placeholder('Search chain').fill(chain_name)
    await expect(np.locator(f'//div[text()="{chain_name}"]')).to_be_visible()
    await element_click(np, '//button[text()="Add to Keplr"]')
    nwp = await get_wallet_page('Keplr')
    if nwp is None:
        raise ValueError('打开钱包失败')
    await element_click(nwp, '//button[div[text()="确定"]]')
    await nwp.close()
    await np.close()


async def role_click(page: Page, role: str,
                     name: Union[str, Pattern[str]] = None,
                     retry: int = 2, delay: int = 0, expect_flag=True):
    logger.info(f'点击元素：{role} name={name}')
    if delay > 0:
        await page.wait_for_timeout(1000 * delay)
    locator = page.get_by_role(role, name=name)
    retry_cnt = 0
    while retry_cnt < retry:
        try:
            if expect_flag:
                await expect(locator).to_be_visible()
            await locator.click()
            return True
        except Exception as e:
            retry_cnt += 1
            logger.error(f'点击元素{role}失败：locator.count()：{await locator.count()}')
            if page.is_closed():
                raise ValueError(f'页面已关闭：{role}')
            await page.wait_for_timeout(100)
    return False

async def element_click(page, selector, delay=0, retry=2, expect_flag=True):
    logger.info(f'点击元素：{selector}')
    if delay > 0:
        await page.wait_for_timeout(1000 * delay)
    locator = page.locator(selector)
    retry_cnt = 0
    while retry_cnt < retry:
        try:
            if expect_flag:
                await expect(locator).to_be_visible()
            await locator.click()
            return True
        except Exception as e:
            retry_cnt += 1
            logger.error(f'点击元素{selector}失败：{await locator.count()}')
            if page.is_closed():
                raise ValueError(f'页面已关闭：{selector}')
            await page.wait_for_timeout(200)
    return False


async def start():
    # if len(browser.background_pages) == 0:
    #     sp = await browser.wait_for_event('backgroundpage')
    # else:
    #     sp = browser.background_pages[0]
    sp = await browser.new_page()
    await sp.goto(f"chrome-extension://{extension_id}/popup.html")
    await element_click(sp, '//input[@type="password"]')
    password = await locator_wait_for(sp, '//input[@type="password"]')
    await password.fill(global_config.get('config', 'password'))
    await element_click(sp, '//button[div[text()="解锁"]]')
    await sp.close()
    # wc = uiautomation.WindowControl(searchDepth=1, Name='Keplr')
    # # 设置为顶层
    # wc.SetTopmost(True)
    # wc.EditControl(searchDepth=1, Name='').SendKey(global_config.get('config', 'password'))
    # wc.ButtonControl(searchDepth=1, Name='解锁').Click()


async def confirm(delay_flag=True):
    if len(browser.background_pages) == 0:
        await browser.wait_for_event('backgroundpage')
    await browser.pages[0].wait_for_timeout(1000)

    bws = list(pygetwindow.getWindowsWithTitle('Keplr'))

    retry_cnt = 0
    while len(bws) == 0 and retry_cnt < 10:
        bws = list(pygetwindow.getWindowsWithTitle('Keplr'))
        await browser.pages[0].wait_for_timeout(800)
        retry_cnt += 1
    if len(bws) > 0:

        bws[0].activate()

        await browser.pages[0].wait_for_timeout(500)
        retry_cnt = 0
        while retry_cnt < 6:
            try:
                confirm_btn = pyautogui.locateCenterOnScreen('confirm.png', confidence=0.9)
                if confirm_btn is not None:
                    await browser.pages[0].wait_for_timeout(200)
                    bws[0].activate()
                    await browser.pages[0].wait_for_timeout(200)
                    pyautogui.click(confirm_btn.x, confirm_btn.y, clicks=1, interval=0.2, duration=0.2, button='left')
                    if delay_flag:
                        await browser.pages[0].wait_for_timeout(10000)
                    return True
            except Exception as e:
                logger.info(e)
                await browser.pages[0].wait_for_timeout(500)
                retry_cnt += 1
    return False