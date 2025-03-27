from .base_data_handler import BaseDataHandler
from typing import List

class NYTimesDataHandler(BaseDataHandler):
    """NYTimes-specific data handler"""
    
    def __init__(self, base_dir: str = "data"):
        super().__init__("NYTimes", base_dir)

    def process_article_links(self, links: List[str]) -> List[str]:
        """Process and deduplicate NYTimes article links"""
        # Filter out non-article links specific to NYTimes
        article_links = [
            link for link in links
            if any(pattern in link for pattern in [
                "/article/", 
                "/interactive/", 
                "/live/",
                "/2025/"  # Specific to your current selector
            ])
        ]
        return article_links 