# List of news websites to crawl
NEWS_SOURCES = [
    "https://www.reuters.com/",
]

# Crawler settings
CRAWLER_SETTINGS = {
    "headless": False,  # Set to True for headless mode
    "days_back": 7,     # Number of days to look back for articles
    "min_delay": 1.0,   # Minimum delay between actions
    "max_delay": 3.0,   # Maximum delay between actions
    "scroll_amount": 500,  # Amount to scroll in pixels
    "timeout": 10,      # Timeout for element waiting
}

# File paths
OUTPUT_DIR = "data"
LOG_DIR = "logs"

# Keywords for filtering content (can be extended)
KEYWORDS = [
    "Ukraine Russia war",
    "Russia Ukraine conflict",
    "Putin Zelensky",
    "Russian invasion",
    "Ukrainian defense",
    "Donbas conflict",
    "Crimea",
    "Kyiv",
    "Moscow",
    "NATO Ukraine",
    "Russian military",
    "Ukrainian military",
    "war crimes",
    "refugees",
    "sanctions"
]

# CSS selectors for different news sites
SITE_SELECTORS = {
    "reuters.com": {
        "article": "article",
        "title": "h1",
        "content": ".article__content"
    },
    
} 