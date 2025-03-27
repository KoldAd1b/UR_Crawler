from typing import Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv

class AuthenticationHandler:
    def __init__(self, driver):
        """
        Initialize with driver and load credentials from environment variables.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        load_dotenv()  # Load environment variables
        self.credentials = self._load_credentials()
        self.authenticated_sites = set()

    def _load_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load credentials from environment variables."""
        return {
            'nytimes.com': {
                'username': os.getenv('NYTIMES_USERNAME'),
                'password': os.getenv('NYTIMES_PASSWORD')
            },
        }

    def authenticate(self, url: str) -> bool:
        """Handle authentication for different sites."""
        domain = self._get_domain(url)
        if domain not in self.credentials or domain in self.authenticated_sites:
            return True

        auth_method = getattr(self, f'_auth_{domain}', self._auth_default)
        return auth_method(self.credentials[domain])

    def _auth_nytimes(self, creds: Dict[str, str]) -> bool:
        """Site specific authentication."""
        try:
            # Click login button
            login_btn = self.driver.find_element(By.CSS_SELECTOR, '.login-button')
            login_btn.click()
            
            # Wait for login form
            self.driver.wait.until(EC.presence_of_element_located((By.ID, 'email')))
            
            # Fill credentials
            email_field = self.driver.find_element(By.ID, 'email')
            password_field = self.driver.find_element(By.ID, 'password')
            
            email_field.send_keys(creds['username'])
            password_field.send_keys(creds['password'])
            
            # Submit form
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, '.submit-button')
            submit_btn.click()
            
            # Wait for authentication
            self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.user-info')))
            
            self.authenticated_sites.add('nytimes.com')
            return True
            
        except Exception as e:
            print(f"NYTimes authentication failed: {str(e)}")
            return False
