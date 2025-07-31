"""
Rate Limiter Utility
Provides rate limiting functionality for API endpoints
"""

import time
from collections import defaultdict, deque
from threading import Lock
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation with sliding window"""
    
    def __init__(self, storage_type='memory'):
        self.storage_type = storage_type
        self.requests = defaultdict(deque)
        self.lock = Lock()
        
        # Default limits
        self.default_limits = {
            'start_diagnostic': 10,  # 10 requests per minute
            'next_question': 30,     # 30 requests per minute
            'submit_answer': 30,     # 30 requests per minute
            'general': 60            # 60 requests per minute
        }
    
    def check_rate_limit(self, identifier, requests_per_minute=None, window_size=60):
        """
        Check if request is within rate limit
        
        Args:
            identifier: User ID or IP address
            requests_per_minute: Maximum requests per minute
            window_size: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        try:
            with self.lock:
                current_time = time.time()
                
                # Get request history for this identifier
                request_history = self.requests[identifier]
                
                # Remove old requests outside the window
                while request_history and current_time - request_history[0] > window_size:
                    request_history.popleft()
                
                # Check if limit exceeded
                if len(request_history) >= requests_per_minute:
                    logger.warning(f"Rate limit exceeded for {identifier}: {len(request_history)} requests")
                    return False
                
                # Add current request
                request_history.append(current_time)
                
                logger.debug(f"Rate limit check passed for {identifier}: {len(request_history)}/{requests_per_minute}")
                return True
                
        except Exception as e:
            logger.error(f"Error in rate limit check: {str(e)}")
            # Allow request on error to prevent blocking
            return True
    
    def get_remaining_requests(self, identifier, requests_per_minute, window_size=60):
        """
        Get remaining requests for identifier
        
        Args:
            identifier: User ID or IP address
            requests_per_minute: Maximum requests per minute
            window_size: Time window in seconds
            
        Returns:
            int: Number of remaining requests
        """
        try:
            with self.lock:
                current_time = time.time()
                request_history = self.requests[identifier]
                
                # Remove old requests
                while request_history and current_time - request_history[0] > window_size:
                    request_history.popleft()
                
                return max(0, requests_per_minute - len(request_history))
                
        except Exception as e:
            logger.error(f"Error getting remaining requests: {str(e)}")
            return requests_per_minute
    
    def reset_limits(self, identifier):
        """
        Reset rate limits for identifier
        
        Args:
            identifier: User ID or IP address
        """
        try:
            with self.lock:
                if identifier in self.requests:
                    del self.requests[identifier]
                    logger.info(f"Reset rate limits for {identifier}")
        except Exception as e:
            logger.error(f"Error resetting rate limits: {str(e)}")
    
    def get_limit_info(self, identifier, requests_per_minute, window_size=60):
        """
        Get detailed rate limit information
        
        Args:
            identifier: User ID or IP address
            requests_per_minute: Maximum requests per minute
            window_size: Time window in seconds
            
        Returns:
            dict: Rate limit information
        """
        try:
            with self.lock:
                current_time = time.time()
                request_history = self.requests[identifier]
                
                # Remove old requests
                while request_history and current_time - request_history[0] > window_size:
                    request_history.popleft()
                
                remaining = max(0, requests_per_minute - len(request_history))
                reset_time = None
                
                if request_history:
                    oldest_request = request_history[0]
                    reset_time = oldest_request + window_size
                
                return {
                    'remaining': remaining,
                    'limit': requests_per_minute,
                    'reset_time': reset_time,
                    'window_size': window_size
                }
                
        except Exception as e:
            logger.error(f"Error getting limit info: {str(e)}")
            return {
                'remaining': requests_per_minute,
                'limit': requests_per_minute,
                'reset_time': None,
                'window_size': window_size
            }
    
    def cleanup_old_entries(self, max_age=3600):
        """
        Clean up old rate limit entries
        
        Args:
            max_age: Maximum age in seconds for entries to keep
        """
        try:
            with self.lock:
                current_time = time.time()
                identifiers_to_remove = []
                
                for identifier, request_history in self.requests.items():
                    # Remove old requests
                    while request_history and current_time - request_history[0] > max_age:
                        request_history.popleft()
                    
                    # Remove empty histories
                    if not request_history:
                        identifiers_to_remove.append(identifier)
                
                # Remove empty entries
                for identifier in identifiers_to_remove:
                    del self.requests[identifier]
                
                if identifiers_to_remove:
                    logger.info(f"Cleaned up {len(identifiers_to_remove)} old rate limit entries")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old entries: {str(e)}")

# Global rate limiter instance
rate_limiter = RateLimiter() 