import os
import logging
import asyncio
from dotenv import load_dotenv
from crawler.base.base_crawler import BaseCrawler
from crawler.sites.nytimes_crawler import NYTimesCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the NYTimes crawler"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize base crawler
        base_crawler = BaseCrawler(headless=False)
        base_crawler.start()

        try:
            # Initialize NYTimes crawler
            nytimes_crawler = NYTimesCrawler(base_crawler)
            
            # Handle authentication and consent
            logger.info("Starting authentication and consent...")
            if not nytimes_crawler.handle_auth():
                logger.error("Authentication failed")
                return
                
            logger.info("Authentication successful. Starting article link extraction...")
            
            # Extract article links
            links_file = await nytimes_crawler.extract_article_links()
            
            if not links_file:
                logger.error("Failed to extract article links")
                return
                
            logger.info(f"Article links saved to: {links_file}")
            
            # Extract article data
            logger.info("Starting article data extraction...")
            articles_file = await nytimes_crawler.extract_all_articles(links_file)
            
            if not articles_file:
                logger.error("Failed to extract article data")
                return
                
            logger.info(f"Article data saved to: {articles_file}")
            
        finally:
            # Clean up
            base_crawler.stop()
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
    