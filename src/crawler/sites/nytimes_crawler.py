import os
from typing import Dict, Optional, Any, List
from ..base.base_site_scraper import BaseSiteScraper, SiteConfig, PaginationType
import logging
from dotenv import load_dotenv
from ..data.base_data_handler import BaseDataHandler

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
        self.data_handler = BaseDataHandler(source_name="NYTimes")
        load_dotenv()

    def handle_auth(self):
        """Handle authentication for NYTimes"""
        try:
            # Navigate to login page
            self.driver.get(self.config.login_url)
            self.driver.random_delay(1.0, 2.0)
            
            # Wait for and fill login form
            email = self.driver.wait_for_element(self.selectors['login_email'])
            password = self.driver.wait_for_element(self.selectors['login_password'])
            
            if not (email and password):
                return False
            
            # Type email with human-like delays
            email.send_keys(os.getenv('NYTIMES_EMAIL')[0])
            for char in os.getenv('NYTIMES_EMAIL')[1:]:
                self.driver.random_delay(0.1, 0.3)
                email.send_keys(char)
            
            # Type password with human-like delays
            password.send_keys(os.getenv('NYTIMES_PASSWORD')[0])
            for char in os.getenv('NYTIMES_PASSWORD')[1:]:
                self.driver.random_delay(0.1, 0.3)
                password.send_keys(char)
            
            # Submit form
            if self.driver.click_element(self.selectors['login_submit']):
                self.driver.random_delay(2.0, 3.0)
                self.handle_consent()
                return True
            return False
            
        except Exception as e:
            logging.error(f"NYTimes authentication failed: {str(e)}")
            return False

    def handle_pagination(self) -> bool:
        """Handle pagination for NYTimes"""
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

    def handle_consent(self) -> bool:
        """Handle consent for NYTimes"""
        try:
            return self.driver.click_element(self.selectors['consent_button'], by="xpath")
        except Exception as e:
            logging.error(f"Consent handling failed: {str(e)}")
            return False

    def get_selectors(self) -> Dict[str, str]:
        """Get NYTimes-specific selectors"""
        return {
            'consent_button': '//*[@id="complianceOverlay"]/div/div/button',
            'login_email': 'input#email',
            'login_password': 'input#password',
            'login_submit': 'button[type="submit"]',
            'login_success': '.user-tools',
            'article_links': 'article a',
            'newsletter_close': '.newsletter-prompt-close',
            'article_title': 'h1[data-testid="headline"]',
            'article_content': 'section[name="articleBody"] p',
            'article_date': 'time'
        }

    async def extract_article_links(self) -> List[str]:
        """Extract and save article links"""
        try:
            links = []
            self.driver.get(self.config.base_url)
            self.driver.random_delay(1.0, 2.5)

            # Scroll and collect links
            for i in range(20):
                logging.info(f"Scrolling {i+1} times")
                self.driver.scroll_to_bottom(scroll_pause=1.0)
                
                elements = self.driver.find_elements(self.selectors['article_links'])
                new_links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]
                links.extend(new_links)
                logging.info(f"Found {len(new_links)} new links")
                
                if not self.handle_pagination():
                    break

            return self.data_handler.save_article_links(links)
            
        except Exception as e:
            logging.error(f"Error getting article links: {str(e)}")
            return None

    async def extract_article_data(self, url: str) -> Dict[str, Any]:
        """Extract data from a single NYTimes article"""
        try:
            self.driver.get(url)
            self.driver.random_delay(1.0, 2.0)
            
            # Scroll to load dynamic content
            self.driver.scroll_to_bottom(scroll_pause=0.5)
            
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
                'source': 'NYTimes'
            }
            
            return processed_data
            
        except Exception as e:
            logging.error(f"Error extracting article data from {url}: {str(e)}")
            return None

    def _extract_title(self) -> Optional[str]:
        """Extract article title"""
        try:
            title_element = self.driver.wait_for_element(self.selectors['article_title'])
            return title_element.text if title_element else None
        except Exception as e:
            logging.error(f"Error extracting title: {str(e)}")
            return None

    def _extract_content(self) -> Optional[str]:
        """Extract article content including hyperlinks"""
        try:
            content_elements = self.driver.find_elements(self.selectors['article_content'])
            if not content_elements:
                return None

            content = []
            for elem in content_elements:
                # Get all child nodes that are links
                links = elem.find_elements("a")
                paragraph_text = elem.text

                # Build map of link text -> href
                for link in links:
                    link_text = link.text
                    href = link.get_attribute("href")
                    if link_text and href:
                        # Replace plain link text with "text (url)"
                        paragraph_text = paragraph_text.replace(link_text, f"{link_text} ({href})")

                content.append(paragraph_text)

            return ' '.join(content)

        except Exception as e:
            logging.error(f"Error extracting content: {str(e)}")
            return None

    def _extract_date(self) -> Optional[str]:
        """Extract article publication date"""
        try:
            date_element = self.driver.wait_for_element(self.selectors['article_date'])
            if date_element:
                date = date_element.get_attribute('datetime') or date_element.text
                return date
            return None
        except Exception as e:
            logging.error(f"Error extracting date: {str(e)}")
            return None 