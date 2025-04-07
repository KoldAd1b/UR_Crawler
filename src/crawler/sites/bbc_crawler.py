import os
from typing import Dict, Optional, Any, List
from ..base.base_site_scraper import BaseSiteScraper, SiteConfig, PaginationType, ContentType
from selenium.webdriver.common.by import By
import logging
from ..handlers.dynamic_content_handler import DynamicContentHandler
from ..handlers.interaction_handler import InteractionHandler
from ..handlers.pagination_handler import PaginationHandler
from ..data.base_data_handler import BaseDataHandler

class BBCCrawler(BaseSiteScraper):
    """BBC-specific crawler implementation with Read More button pagination"""
    
    def __init__(self, base_crawler):
        config = SiteConfig(
            name="BBC",
            base_url="https://www.bbc.com/news/world/europe",
            selectors=self.get_selectors(),
            pagination_type=PaginationType.BUTTON,
            content_type=ContentType.DYNAMIC,
            requires_auth=False,
            rate_limits={"requests_per_minute": 20}
        )
        super().__init__(base_crawler, config)
        self.selectors = self.get_selectors()
        self.driver = base_crawler.driver
        self.data_handler = BaseDataHandler(source_name="BBC")
        self.max_pages = 5  # Limit number of pages to crawl

    def handle_pagination(self) -> bool:
        """Handle BBC-specific pagination using Read More button"""
        try:
            # Find and click the "Load More" button
            load_more_button = self.driver.find_element(
                By.CSS_SELECTOR,
                self.selectors['load_more']
            )
            
            if not load_more_button or not load_more_button.is_displayed():
                return False
                
            # Click the button and wait for content to load
            self.driver.execute_script("arguments[0].click();", load_more_button)
            self.driver.random_delay(2.0, 3.0)
            
            # Check if new content was loaded
            articles = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['article'])
            return len(articles) > 0
            
        except Exception as e:
            logging.error(f"Pagination failed: {str(e)}")
            return False

    def handle_dynamic_content(self) -> bool:
        """Handle BBC-specific dynamic content"""
        interaction_handler = InteractionHandler(self.driver)
        try:
            # Handle cookie consent if present
            consent_button = interaction_handler.wait_for_element(
                self.selectors['consent_button'],
                type="css"
            )
            if consent_button:
                consent_button.click()
                self.driver.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            logging.error(f"Dynamic content handling failed: {str(e)}")
            return False

    def get_selectors(self) -> Dict[str, str]:
        """Get BBC-specific selectors"""
        return {
            'consent_button': 'button[data-testid="consent-accept"]',
            'article': 'article',
            'article_links': 'article a',
            'article_title': 'h1[data-testid="heading"]',
            'article_content': 'article p',
            'article_date': 'time',
            'load_more': 'button[data-testid="load-more"]'
        }

    async def extract_article_links(self) -> List[str]:
        """Extract and save article links"""
        interaction_handler = InteractionHandler(self.driver)
        try:
            links = []
            self.driver.get(self.config.base_url)
            self.driver.random_delay(1.0, 2.0)

            # Handle initial dynamic content
            self.handle_dynamic_content()

            # Extract links from multiple pages
            for _ in range(self.max_pages):
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    self.selectors['article_links']
                )
                new_links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]
                links.extend(new_links)
                
                if not self.handle_pagination():
                    break

            return self.data_handler.save_article_links(links)
            
        except Exception as e:
            logging.error(f"Error getting article links: {str(e)}")
            return None

    async def extract_article_data(self, url: str) -> Dict[str, Any]:
        """Extract data from a single BBC article"""
        try:
            self.driver.get(url)
            self.driver.random_delay(1.0, 2.0)
            
            # Extract article metadata
            title = self._extract_title()
            content = self._extract_content()
            date = self._extract_date()
            
            if not all([title, content, date]):
                logging.warning(f"Failed to extract required data from article: {url}")
                return None
                
            processed_data = {
                'url': url,
                'title': title.strip(),
                'content': content.strip(),
                'date': date,
                'source': 'BBC'
            }
            
            return processed_data
            
        except Exception as e:
            logging.error(f"Error extracting article data from {url}: {str(e)}")
            return None

    def _extract_title(self) -> Optional[str]:
        """Extract article title"""
        try:
            title_element = self.driver.wait_for_element(
                self.selectors['article_title'],
                type="css"
            )
            return title_element.text if title_element else None
        except Exception as e:
            logging.error(f"Error extracting title: {str(e)}")
            return None

    def _extract_content(self) -> Optional[str]:
        """Extract article content"""
        try:
            content_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.selectors['article_content']
            )
            if not content_elements:
                return None
                
            content = ' '.join([elem.text for elem in content_elements if elem.text])
            return content
        except Exception as e:
            logging.error(f"Error extracting content: {str(e)}")
            return None

    def _extract_date(self) -> Optional[str]:
        """Extract article publication date"""
        try:
            date_element = self.driver.wait_for_element(
                self.selectors['article_date'],
                type="css"
            )
            if date_element:
                date = date_element.get_attribute('datetime') or date_element.text
                return date
            return None
        except Exception as e:
            logging.error(f"Error extracting date: {str(e)}")
            return None 