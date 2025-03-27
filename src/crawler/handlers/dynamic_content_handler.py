import logging
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random

class DynamicContentHandler:
    def __init__(self, driver):
        self.driver = driver

    def handle_read_more(self, selectors: List[str]) -> bool:
        """Handle 'Read More' buttons."""
        try:
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(random.uniform(1, 2))
            return True
        except Exception as e:
            print(f"Error handling read more: {str(e)}")
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
            print(f"Error during scrolling: {str(e)}")
            return False 
        
   