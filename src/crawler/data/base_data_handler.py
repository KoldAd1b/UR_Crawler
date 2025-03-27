import json
import csv
import pandas as pd
from typing import List, Dict, Optional, Any
import logging
import os
from datetime import datetime
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin

class BaseDataHandler(ABC):
    """Base class for handling data extraction and storage for news articles"""
    
    def __init__(self, source_name: str, base_dir: str = "data"):
        self.source_name = source_name
        self.base_dir = os.path.join(base_dir, source_name.lower())
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "links"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "articles"), exist_ok=True)

    def _generate_filename(self, prefix: str) -> str:
        """Generate a filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.source_name}_{prefix}_{timestamp}"

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to prevent duplicates due to different URL formats"""
        parsed = urlparse(url)
        # Remove query parameters and fragments
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def _clean_links(self, links: List[str]) -> pd.DataFrame:
        """Clean and preprocess links"""
        if not links:
            return pd.DataFrame(columns=['article_url', 'normalized_url'])
        
        # Create DataFrame with original and normalized URLs
        df = pd.DataFrame({
            'article_url': links,
            'normalized_url': [self._normalize_url(url) for url in links]
        })
        
        # Remove duplicates based on normalized URLs
        df = df.drop_duplicates(subset='normalized_url', keep='first')
        
        # Remove invalid URLs
        df = df[df['article_url'].notna()]
        
        return df

    @abstractmethod
    def process_article_links(self, links: List[str]) -> pd.DataFrame:
        """Process and deduplicate article links based on source-specific rules"""
        pass

    def save_article_links(self, links: List[str], format: str = "json") -> str:
        """Save article links to file using pandas with preprocessing"""
        try:
            # Clean and process links
            cleaned_df = self._clean_links(links)
            processed_df = self.process_article_links(cleaned_df['article_url'].tolist())
            
            if processed_df.empty:
                logging.warning("No valid links to save after processing")
                return None
            
            # Generate filename and save
            filename = self._generate_filename("article_links")
            filepath = os.path.join(self.base_dir, "links", f"{filename}.{format}")
            
            if format.lower() == "json":
                processed_df.to_json(filepath, orient='records', indent=2)
            else:
                processed_df.to_csv(filepath, index=False)

            logging.info(f"Saved {len(processed_df)} links to {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"Error saving article links: {str(e)}")
            return None

    def save_article_data(self, articles: List[Dict[str, Any]], format: str = "json") -> str:
        """Save article data to file using pandas with data validation"""
        if not articles:
            logging.warning("No articles to save")
            return None
            
        try:
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(articles)
            
            # Basic data validation
            required_columns = {'url', 'title', 'content', 'date', 'source'}
            if not all(col in df.columns for col in required_columns):
                missing = required_columns - set(df.columns)
                logging.error(f"Missing required columns: {missing}")
                return None
            
            # Remove duplicates based on URL
            df['normalized_url'] = df['url'].apply(self._normalize_url)
            df = df.drop_duplicates(subset='normalized_url', keep='first')
            df = df.drop(columns=['normalized_url'])
            
            # Remove rows with missing essential data
            df = df.dropna(subset=['title', 'content'])
            
            if df.empty:
                logging.warning("No valid articles to save after preprocessing")
                return None
            
            # Save to file
            filename = self._generate_filename("articles")
            filepath = os.path.join(self.base_dir, "articles", f"{filename}.{format}")
            
            if format.lower() == "json":
                df.to_json(filepath, orient='records', indent=2)
            else:
                df.to_csv(filepath, index=False)

            logging.info(f"Saved {len(df)} articles to {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"Error saving article data: {str(e)}")
            return None

    def load_article_links(self, filepath: str) -> List[str]:
        """Load article links from file using pandas with validation"""
        try:
            if filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                df = pd.read_csv(filepath)
            
            # Ensure required column exists
            if 'article_url' not in df.columns:
                logging.error("Invalid file format: 'article_url' column not found")
                return []
            
            # Clean and validate URLs
            valid_urls = df['article_url'].dropna().tolist()
            return valid_urls

        except Exception as e:
            logging.error(f"Error loading article links: {str(e)}")
            return [] 