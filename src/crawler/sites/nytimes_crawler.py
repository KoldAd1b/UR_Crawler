import os
from typing import Dict, Optional, Any, List
from ..base.base_site_scraper import BaseSiteScraper, SiteConfig, PaginationType
from selenium.webdriver.common.by import By
import logging
from dotenv import load_dotenv
from ..handlers.dynamic_content_handler import DynamicContentHandler
from ..handlers.interaction_handler import InteractionHandler
from ..handlers.pagination_handler import PaginationHandler
from ..handlers.authentication_handler import AuthenticationHandler
from ..handlers.nytimes_data_handler import NYTimesDataHandler

class NYTimesCrawler(BaseSiteScraper):
    """NYTimes-specific crawler implementation"""
    
    def __init__(self, base_crawler):
        config = SiteConfig(
            name="NYTimes",
            base_url="https://www.nytimes.com/news-event/ukraine-russia",
            login_url="https://myaccount.nytimes.com/auth/login",
            pagination_type=PaginationType.INFINITE_SCROLL,
            required_login=True,
            dynamic_loading=True,
            rate_limit=2.0
        )
        super().__init__(base_crawler, config)
        self.selectors = self.get_selectors()
        self.driver = base_crawler.driver
        self.data_handler = NYTimesDataHandler()
        load_dotenv()

    def handle_auth(self):
        """Return NYTimes-specific authentication handler"""
        try:
                # Navigate to login page
                self.driver.get(self.config.login_url)
                
                # Wait for and fill login form
                email = self.driver.wait_for_element(self.selectors['login_email'])
                password = self.driver.wait_for_element(self.selectors['login_password'])
                
                if not (email and password):
                    return False
                
                
                email.send_keys(os.getenv('NYTIMES_EMAIL')[0])
                for char in os.getenv('NYTIMES_EMAIL')[1:]:
                    self.driver.random_delay(0.1, 0.3)  # Simulate human typing delay
                    email.send_keys(char)
                
                password.send_keys(os.getenv('NYTIMES_PASSWORD')[0])
                for char in os.getenv('NYTIMES_PASSWORD')[1:]:
                    self.driver.random_delay(0.1, 0.3)  # Simulate human typing delay
                    password.send_keys(char)
               
                
                # Submit form
                submit = self.driver.wait_for_element(self.selectors['login_submit'])
                if submit:
                    submit.click()
                    # Wait for successful login indicator
                    return bool(self.driver.wait_for_element(self.selectors['login_success']))
                return False
                
        except Exception as e:
                logging.error(f"NYTimes authentication failed: {str(e)}")
                return False
                
   

    def handle_pagination(self) :
        """Return NYTimes-specific pagination handler"""
        try:
                # NYTimes uses infinite scroll
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.execute_script(f"window.scrollTo(0, {last_height});")
                self.driver.random_delay(1.0, 2.0)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                return new_height > last_height
                
        except Exception as e:
                logging.error(f"Pagination failed: {str(e)}")
                return False
                
       

    def handle_dynamic_content(self) :
        """Return NYTimes-specific dynamic content handler"""
        interaction_handler = InteractionHandler(self.driver)
        try:
            interaction_handler.click_element(self.selectors['consent_button'],type="xpath")                   
        except Exception as e:
                logging.error(f"Dynamic content handling failed: {str(e)}")
                return False
                
                

    def get_selectors(self) -> Dict[str, str]:
        """Get NYTimes-specific selectors"""
        return {
            'consent_button': '//*[@id="complianceOverlay"]/div/div/button',
            'login_email': 'input#email',
            'login_password': 'input#password',
            'login_submit': 'button[type="submit"]',
            'login_success': '.user-tools',
            'article_links': 'article a[href*="/2025/"]',
            'newsletter_close': '.newsletter-prompt-close',
            'article_title': 'h1[data-testid="headline"]',
            'article_content': 'section[name="articleBody"] p',
            'article_date': 'time'
        }


    async def extract_article_links(self) -> str:
        """Extract and save article links"""
        interaction_handler = InteractionHandler(self.driver)
        try:
            links = []
            self.crawler.get_page(self.config.base_url)
            
            # Handle initial dynamic content
            self.dynamic_handler(self.driver, self.get_selectors())
            self.driver.random_delay(1.0, 2.5)

            # Scroll and collect links
            for i in range(15):
                print(f"Scrolling {i+1} times")
                interaction_handler.scroll_random(amount=300, type="down")
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    self.get_selectors()['article_links']
                )
                new_links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]
                links.extend(new_links)
                print(f"Found {len(new_links)} new links")
                if not self.pagination_handler(self.driver, self.get_selectors()):
                    break

            # Save links to file
            return self.data_handler.save_article_links(links)
            
        except Exception as e:
            logging.error(f"Error getting article links: {str(e)}")
            return None

    async def extract_all_articles(self, links_file: str) -> str:
        """Extract data from all articles in the links file"""
        try:
            # First ensure we're logged in
            if not self.handle_auth():
                raise Exception("Failed to authenticate")

            # Load links
            links = self.data_handler.load_article_links(links_file)
            articles_data = []

            # Extract data from each article
            for link in links:
                article_data = await self.extract_article_data(link)
                if article_data:
                    articles_data.append(article_data)
                self.driver.random_delay(1.0, 2.0)  # Prevent rate limiting

            # Save articles data
            return self.data_handler.save_article_data(articles_data)

        except Exception as e:
            logging.error(f"Error extracting articles: {str(e)}")
            return None 