from typing import Callable
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from config import KeyscoreConfig
from loguru import logger
import time
import sys

if "-h" not in sys.argv and "--help" not in sys.argv:
    logger.info("Initializing Selenium Driver...")
    _CHROME_DRIVER_OPTIONS = webdriver.ChromeOptions()
    _CHROME_DRIVER_OPTIONS.add_argument("--ignore-certificate-errors")
    _CHROME_DRIVER_OPTIONS.add_argument("--incognito")
    _CHROME_DRIVER_OPTIONS.add_argument("--headless")
    _CHROME_DRIVER_OPTIONS.add_argument("--disable-dev-shm-usage")
    _CHROME_DRIVER_OPTIONS.add_argument("--no-sandbox")
    _CHROME_DRIVER = webdriver.Chrome(options=_CHROME_DRIVER_OPTIONS)
    logger.info("Selenium Driver initialized.")

    _MAX_CHECK_LOOP_ITER = 5

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
        loaded = False
        load_attempts = 0
        while loaded == False:
            try:
                loaded = load_check(_CHROME_DRIVER)
            except WebDriverException:
                pass
            finally:
                time.sleep(KeyscoreConfig.get("html_default_wait"))
                load_attempts = load_attempts + 1
                if load_attempts == _MAX_CHECK_LOOP_ITER:
                    logger.debug(f"Page source: {_CHROME_DRIVER.page_source}")
                    raise Exception(f"Load Check failed {load_attempts} times")
    
    # Perform actions on website as defined by caller
    if post_load is not None:
        try:
            post_load(_CHROME_DRIVER)
            # Check if site has loaded stuff caused by actions before
            if ready_check is not None:
                ready = False
                ready_attempts = 0
                while ready == False:
                    try:
                        ready = ready_check(_CHROME_DRIVER)
                    except WebDriverException:
                        pass
                    finally:
                        time.sleep(KeyscoreConfig.get("html_default_wait"))
                        ready_attempts = ready_attempts + 1
                        if ready_attempts == _MAX_CHECK_LOOP_ITER:
                            logger.debug(f"Page source: {_CHROME_DRIVER.page_source}")
                            raise Exception(f"Ready Check failed {ready_attempts} times")
        except WebDriverException:
            pass
    
    page_src = _CHROME_DRIVER.page_source
    return BeautifulSoup(page_src, 'lxml')