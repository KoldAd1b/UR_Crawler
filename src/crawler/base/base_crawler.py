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
                no_sandbox=True,
            )
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
        except Exception as e:
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
                self.session_start_time = None

    def random_delay(self, min_delay: float, max_delay: float):
        """Add a random delay between actions."""
        time.sleep(random.uniform(min_delay, max_delay))

    def wait_for_element(self, selector: str, by: str = "css", timeout: int = 10):
        """Wait for an element to be present and visible."""
        try:
            if by == "css":
                return self.driver.wait_for_element(selector, timeout=timeout)
            elif by == "xpath":
                return self.driver.wait_for_xpath(selector, timeout=timeout)
            else:
                raise ValueError(f"Unsupported selector type: {by}")
        except Exception as e:
            logging.warning(f"Element not found: {selector}")
            return None

    def click_element(self, selector: str, by: str = "css") -> bool:
        """Click an element safely."""
        try:
            if by == "css":
                self.driver.click(selector)
            elif by == "xpath":
                self.driver.click_xpath(selector)
            else:
                raise ValueError(f"Unsupported selector type: {by}")
            return True
        except Exception as e:
            logging.error(f"Failed to click element: {str(e)}")
            return False

    def scroll_to_bottom(self, scroll_pause: float = 1.0, max_scrolls: int = 10) -> bool:
        """Scroll to bottom of page gradually."""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scrolls = 0
            
            while scrolls < max_scrolls:
                # Scroll down gradually
                current_height = 0
                target_height = last_height * (scrolls + 1) / max_scrolls
                
                while current_height < target_height:
                    current_height += random.randint(100, 300)
                    self.driver.execute_script(f"window.scrollTo(0, {min(current_height, target_height)});")
                    time.sleep(random.uniform(0.1, 0.3))
                
                time.sleep(scroll_pause)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scrolls += 1
                
            return True
            
        except Exception as e:
            logging.error(f"Error during scrolling: {str(e)}")
            return False
    