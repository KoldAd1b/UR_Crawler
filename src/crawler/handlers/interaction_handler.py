from typing import Any, Dict, Optional, Callable
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import random

class InteractionHandler:
    """Base class for all handlers"""
    
    def __init__(self, driver):
        self.driver = driver

    def execute_with_retry(self, action: Callable, max_retries: int = 3) -> Optional[Any]:
        """Execute an action with retry logic"""
        for attempt in range(max_retries):
            try:
                return action()
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logging.error(f"All attempts failed: {str(e)}")
                    return None

    def wait_for_element(self, selector: str, timeout: int = 10,type:str = "css"):
        """Wait for element to be present and visible"""
        try:
            if type == "css":
                return self.driver.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            elif type == "xpath":
                return self.driver.wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
        except Exception as e:
            logging.warning(f"Element not found: {selector}")
            return None

    def click_element(self, selector: str) -> bool:
        """Click an element safely"""
        element = self.wait_for_element(selector)
        if element and element.is_displayed():
            try:
                element.click()
                return True
            except:
                # Fallback to JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as e:
                    logging.error(f"Failed to click element: {str(e)}")
        return False 
    
    def random_delay(self,min:float,max:float):
        """Random delay"""
        time.sleep(random.uniform(min,max))

    def scroll_random(self,amount:int,type:str):
        """Scroll page by random increments."""
        try:
            # Scroll down by a random amount
            scroll_amount = random.randint(amount,amount + 300)  # Randomly choose a scroll amount
            if type == "down":
                self.driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
            else:
                self.driver.execute_script(f"window.scrollTo(0, -{scroll_amount});")
            time.sleep(random.uniform(0.1, 0.2))

            self.random_delay(0.5, 1.0)

        except Exception as e:
            logging.error(f"Error during scrolling up: {str(e)}")        