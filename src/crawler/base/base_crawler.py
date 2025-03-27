from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from seleniumbase import Driver
import random
import time
import logging
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseCrawler:
    """Base crawler with common utilities and browser management."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.ua = UserAgent()
        self.session_start_time = None
        self.max_session_duration = 3600  # 1 hour

    def start(self):
        """Initialize the browser with anti-detection measures."""
        try:
            self.driver = Driver(
                uc=True,
                headless=self.headless,
                undetectable=True,
                incognito=True,
                block_images=True,
                disable_gpu=True,
                disable_dev_shm_usage=True,
                no_sandbox=True,
                user_agent=self.ua.random
            )
            self.wait = WebDriverWait(self.driver, 10)
            self.session_start_time = time.time()
            logging.info("Browser started successfully")
        except Exception as e:
            logging.error(f"Failed to start browser: {str(e)}")
            raise

    def check_session_validity(self) -> bool:
        """Check if the current session is still valid."""
        if not self.session_start_time:
            return False
        return (time.time() - self.session_start_time) < self.max_session_duration

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_page(self, url: str) -> bool:
        """Load a page with retry mechanism and error handling."""
        try:
            if not self.check_session_validity():
                self.restart_session()
            
            self.driver.get(url)
            self.random_delay(1.0, 2.0)
            return True
        except WebDriverException as e:
            logging.error(f"Failed to load page {url}: {str(e)}")
            raise

    def restart_session(self):
        """Restart the browser session."""
        self.stop()
        self.start()

    def stop(self):
        """Clean up browser resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error while stopping browser: {str(e)}")
            finally:
                self.driver = None
                self.wait = None
                self.session_start_time = None
    