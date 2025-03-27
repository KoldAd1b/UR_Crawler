from typing import List, Dict, Set
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextProcessor:
    def __init__(self, keywords: List[str]):
        """
        Initialize text processor with keywords.
        
        Args:
            keywords: List of keywords to check against
        """
        # Create keyword sets for faster lookup
        self.keyword_set = set(keyword.lower() for keyword in keywords)
        
        # Create TF-IDF vectorizer for semantic similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Create keyword vectors for comparison
        keyword_text = ' '.join(keywords)
        self.keyword_vector = self.vectorizer.fit_transform([keyword_text])
        
    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """
        Extract key phrases from text using simple heuristics.
        
        Args:
            text: Text to extract phrases from
            max_phrases: Maximum number of phrases to extract
            
        Returns:
            List of key phrases
        """
        # Convert to lowercase and split into words
        words = text.lower().split()
        
        # Create bigrams and trigrams
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        # Count frequencies
        phrase_counts = Counter(bigrams + trigrams)
        
        # Return top phrases
        return [phrase for phrase, _ in phrase_counts.most_common(max_phrases)]
        
    def calculate_relevance(self, title: str, content: str) -> float:
        """
        Calculate relevance score using multiple metrics.
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Relevance score between 0 and 1
        """
        # Combine title and content
        text = f"{title} {content}".lower()
        
        # 1. Keyword presence in title (weighted higher)
        title_keywords = sum(1 for keyword in self.keyword_set if keyword in title.lower())
        title_score = min(title_keywords / len(self.keyword_set), 1.0)
        
        # 2. Extract and check key phrases
        key_phrases = self.extract_key_phrases(text)
        phrase_score = sum(1 for phrase in key_phrases if any(keyword in phrase for keyword in self.keyword_set)) / len(key_phrases)
        
        # 3. Calculate semantic similarity
        try:
            text_vector = self.vectorizer.transform([text])
            similarity_score = cosine_similarity(text_vector, self.keyword_vector)[0][0]
        except:
            similarity_score = 0.0
            
        # Combine scores with weights
        weights = [0.4, 0.3, 0.3]  # Title, phrases, semantic
        scores = [title_score, phrase_score, similarity_score]
        
        return np.average(scores, weights=weights)
        
    def is_relevant(self, title: str, content: str, threshold: float = 0.3) -> bool:
        """
        Determine if content is relevant based on multiple metrics.
        
        Args:
            title: Article title
            content: Article content
            threshold: Minimum relevance score
            
        Returns:
            bool indicating if content is relevant
        """
        relevance_score = self.calculate_relevance(title, content)
        return relevance_score >= threshold 