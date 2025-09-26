"""Session management utilities."""

import requests_cache
from retry_requests import retry
from ..config.settings import CACHE_DIR, CACHE_EXPIRE_AFTER


class SessionManager:
    """
    Manages HTTP sessions with caching and retry logic.
    
    This class provides a centralized way to manage HTTP sessions with
    built-in caching and retry functionality for API requests.
    """
    
    def __init__(self, api_config):
        """
        Initialize session manager.
        
        Parameters
        ----------
        api_config : dict
            API configuration object containing retry and cache settings
        """
        self.api_config = api_config
        self._session = None
    
    @property
    def session(self):
        """
        Get or create cached session with retry logic.
        
        Returns
        -------
        requests.Session
            Cached session with retry functionality
        """
        if self._session is None:
            cache_session = requests_cache.CachedSession(
                CACHE_DIR, 
                expire_after=CACHE_EXPIRE_AFTER
            )
            self._session = retry(
                cache_session, 
                retries=self.api_config['retry_count'],
                backoff_factor=self.api_config['backoff_factor']
            )
        return self._session
    
    def reset(self):
        """Reset the session (useful for testing)."""
        self._session = None