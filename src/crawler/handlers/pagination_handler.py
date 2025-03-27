from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random

class PaginationHandler:
    def __init__(self, driver):
        self.driver = driver
        self.current_page = 1

    async def handle_pagination(self, selectors: dict, max_pages: int = 5) -> bool:
        """
        Handle different types of pagination.
        
        Args:
            selectors: Dict containing pagination selectors
            max_pages: Maximum number of pages to process
        """
        pagination_type = self._detect_pagination_type(selectors)
        
        if pagination_type == "button":
            return await self._handle_button_pagination(selectors, max_pages)
        elif pagination_type == "infinite_scroll":
            return await self._handle_infinite_scroll(max_pages)
        else:
            return False

    def _detect_pagination_type(self, selectors: dict) -> str:
        """Detect the type of pagination on the page."""
        try:
            # Check for next button
            if self.driver.find_elements(By.CSS_SELECTOR, selectors.get('next_button', '')):
                return "button"
            
            # Check for infinite scroll
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height > scroll_height:
                return "infinite_scroll"
                
            return "unknown"
            
        except Exception:
            return "unknown"

    async def _handle_button_pagination(self, selectors: dict, max_pages: int) -> bool:
        """Handle button-based pagination."""
        try:
            while self.current_page < max_pages:
                next_button = self.driver.find_element(By.CSS_SELECTOR, selectors['next_button'])
                
                if not next_button.is_enabled():
                    break
                    
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(random.uniform(2, 4))
                self.current_page += 1
                
            return True
            
        except Exception as e:
            print(f"Error in button pagination: {str(e)}")
            return False 