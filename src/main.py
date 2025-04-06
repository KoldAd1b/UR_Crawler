import asyncio
import logging
from crawler.base.base_crawler import BaseCrawler
from crawler.sites.nytimes_crawler import NYTimesCrawler
import json
from datetime import datetime

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def main():
    """Main execution function."""
    setup_logging()
    logging.info("Starting NYTimes News Crawler")
    
    crawler = None
    try:
        # Initialize base crawler
        base_crawler = BaseCrawler(headless=False)
       
        
        # Initialize NYTimes-specific crawler
        crawler = NYTimesCrawler(base_crawler)

        # The flow should be like this

        # Initialize the crawler
        crawler.start()

        # 1. Consent to policy 
        crawler.handle_dynamic_content()

        # 2. Login
        if(crawler.config.requires_auth):
            crawler.handle_authentication()

        # 3. Get article links
        crawler.handle_pagination()

        # 4. Extract article data
        crawler.extract_article_data()

        # 5. Save results

    
        # Get article links from main page
        articles = await crawler.get_article_links()
        logging.info(f"Found {len(articles)} articles")
        
        # Process articles
        results = []
        for url in articles:
            if article_data := await crawler.extract_article_data(url):
                results.append(article_data)
                
        # Save results
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"data/nytimes_articles_{timestamp}.json", "w") as f:
                json.dump(results, f, indent=2)
                
        logging.info(f"Successfully processed {len(results)} articles")
            
    except Exception as e:
        logging.error(f"Error during crawling: {str(e)}")
        
    finally:
        if crawler:
            crawler.crawler.stop()

if __name__ == "__main__":
    asyncio.run(main()) 
    