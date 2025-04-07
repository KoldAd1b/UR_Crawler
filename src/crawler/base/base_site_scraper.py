from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class PaginationType(Enum):
    BUTTON = "button"
    INFINITE_SCROLL = "infinite_scroll"
    NUMBERED = "numbered"
    NONE = "none"

class ContentType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"

@dataclass
class SiteConfig:
    """Configuration for site-specific implementation"""
    name: str
    login_url: str = None
    base_url: str
    selectors: Dict[str, str]
    pagination_type: PaginationType
    content_type: ContentType
    requires_auth: bool = False
    rate_limits: Dict[str, int] = None

class BaseSiteScraper(ABC):
    """Abstract base class for site-specific scrapers"""
    
    def __init__(self, crawler, config: SiteConfig):
        self.crawler = crawler
        self.config = config

    
    
