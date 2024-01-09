from typing import Callable
from selenium import webdriver
from bs4 import BeautifulSoup
from config import KeyscoreConfig
from loguru import logger
import time

logger.info("Initializing Selenium Driver...")
_CHROME_DRIVER_OPTIONS = webdriver.ChromeOptions()
_CHROME_DRIVER_OPTIONS.add_argument("--ignore-certificate-errors")
_CHROME_DRIVER_OPTIONS.add_argument("--incognito")
_CHROME_DRIVER_OPTIONS.add_argument("--headless")
_CHROME_DRIVER = webdriver.Chrome(options=_CHROME_DRIVER_OPTIONS)
logger.info("Selenium Driver initialized.")

def get_bs_for_url(
        url: str,
        load_check: Callable[[webdriver.Chrome], bool] = None,
        post_load: Callable[[webdriver.Chrome], any] = None,
        ready_check: Callable[[webdriver.Chrome], bool] = None
    ):
    _CHROME_DRIVER.get(url)
    time.sleep(KeyscoreConfig.get("html_default_wait"))

    # Check if the site has initially loaded
    if load_check is not None:
        while(load_check(_CHROME_DRIVER) == False):
            time.sleep(KeyscoreConfig.get("html_default_wait"))
    
    # Perform actions on website as defined by caller
    if post_load is not None:
        post_load(_CHROME_DRIVER)

    # Check if site has loaded stuff caused by actions before
    if ready_check is not None:
        while(ready_check(_CHROME_DRIVER) == False):
            time.sleep(KeyscoreConfig.get("html_default_wait"))
    
    page_src = _CHROME_DRIVER.page_source
    return BeautifulSoup(page_src, 'lxml')