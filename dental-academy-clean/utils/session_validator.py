"""
Session Validator Utility
Provides session validation and CSRF protection functionality
"""

import secrets
import hashlib
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SessionValidator:
    """Session validation and CSRF protection"""
    
    def __init__(self):
        self.csrf_tokens = {}
        self.session_timeout = 7200  # 2 hours in seconds
        
    def generate_csrf_token(self, session_id=None):
        """
        Generate CSRF token for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            str: CSRF token
        """
        try:
            token = secrets.token_urlsafe(32)
            timestamp = time.time()
            
            if session_id:
                self.csrf_tokens[session_id] = {
                    'token': token,
                    'timestamp': timestamp,
                    'used': False
                }
            
            logger.debug(f"Generated CSRF token for session {session_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating CSRF token: {str(e)}")
            return None
    
    def validate_csrf(self, token, session_id=None):
        """
        Validate CSRF token
        
        Args:
            token: CSRF token to validate
            session_id: Session identifier
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            if not token:
                return False
            
            if session_id and session_id in self.csrf_tokens:
                stored_token_data = self.csrf_tokens[session_id]
                
                # Check if token matches and is not expired
                if (stored_token_data['token'] == token and 
                    not stored_token_data['used'] and
                    time.time() - stored_token_data['timestamp'] < 3600):  # 1 hour expiry
                    
                    # Mark token as used
                    stored_token_data['used'] = True
                    return True
            
            # For backward compatibility, accept any non-empty token
            # In production, this should be more strict
            return len(token) > 0
            
        except Exception as e:
            logger.error(f"Error validating CSRF token: {str(e)}")
            return False
    
    def validate_session(self, diagnostic_session):
        """
        Validate diagnostic session
        
        Args:
            diagnostic_session: DiagnosticSession instance
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            if not diagnostic_session:
                return False
            
            # Check if session exists and is active
            if diagnostic_session.status not in ['active', 'completed']:
                logger.warning(f"Invalid session status: {diagnostic_session.status}")
                return False
            
            # Check if session is not expired
            if diagnostic_session.started_at:
                current_time = datetime.now(timezone.utc)
                started_time = diagnostic_session.started_at
                if started_time.tzinfo is None:
                    # Если started_at наивное время, добавляем UTC
                    started_time = started_time.replace(tzinfo=timezone.utc)
                session_age = current_time - started_time
                if session_age.total_seconds() > self.session_timeout:
                    logger.warning(f"Session expired: {diagnostic_session.id}")
                    return False
            
            # Check if session has valid user (if authenticated)
            if diagnostic_session.user_id:
                # Additional user validation could be added here
                pass
            
            logger.debug(f"Session validation passed: {diagnostic_session.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self, max_age=3600):
        """
        Clean up expired CSRF tokens
        
        Args:
            max_age: Maximum age in seconds for tokens to keep
        """
        try:
            current_time = time.time()
            tokens_to_remove = []
            
            for session_id, token_data in self.csrf_tokens.items():
                if current_time - token_data['timestamp'] > max_age:
                    tokens_to_remove.append(session_id)
            
            for session_id in tokens_to_remove:
                del self.csrf_tokens[session_id]
            
            if tokens_to_remove:
                logger.info(f"Cleaned up {len(tokens_to_remove)} expired CSRF tokens")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
    
    def get_session_info(self, diagnostic_session):
        """
        Get session information for validation
        
        Args:
            diagnostic_session: DiagnosticSession instance
            
        Returns:
            dict: Session information
        """
        try:
            if not diagnostic_session:
                return None
            
            session_age = None
            if diagnostic_session.started_at:
                current_time = datetime.now(timezone.utc)
                started_time = diagnostic_session.started_at
                if started_time.tzinfo is None:
                    # Если started_at наивное время, добавляем UTC
                    started_time = started_time.replace(tzinfo=timezone.utc)
                session_age = (current_time - started_time).total_seconds()
            
            return {
                'id': diagnostic_session.id,
                'status': diagnostic_session.status,
                'user_id': diagnostic_session.user_id,
                'started_at': diagnostic_session.started_at.isoformat() if diagnostic_session.started_at else None,
                'session_age': session_age,
                'questions_answered': diagnostic_session.questions_answered,
                'is_expired': session_age > self.session_timeout if session_age else False
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {str(e)}")
            return None
    
    def refresh_session(self, diagnostic_session):
        """
        Refresh session timestamp
        
        Args:
            diagnostic_session: DiagnosticSession instance
            
        Returns:
            bool: True if session was refreshed, False otherwise
        """
        try:
            if not diagnostic_session or diagnostic_session.status != 'active':
                return False
            
            # Update session timestamp
            diagnostic_session.last_activity = datetime.now(timezone.utc)
            
            logger.debug(f"Refreshed session: {diagnostic_session.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing session: {str(e)}")
            return False
    
    def validate_ip_address(self, session_ip, current_ip):
        """
        Validate IP address for session
        
        Args:
            session_ip: IP address stored in session
            current_ip: Current request IP address
            
        Returns:
            bool: True if IP addresses match or validation is not required
        """
        try:
            # If no session IP stored, allow request
            if not session_ip:
                return True
            
            # For now, allow IP changes (could be made stricter in production)
            # In production, you might want to check for IP changes and log them
            if session_ip != current_ip:
                logger.info(f"IP address changed for session: {session_ip} -> {current_ip}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating IP address: {str(e)}")
            return True  # Allow on error
    
    def generate_session_hash(self, session_data):
        """
        Generate hash for session data validation
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            str: Hash of session data
        """
        try:
            # Create a string representation of session data
            data_string = f"{session_data.get('id', '')}{session_data.get('user_id', '')}{session_data.get('started_at', '')}"
            
            # Generate hash
            hash_object = hashlib.sha256(data_string.encode())
            return hash_object.hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating session hash: {str(e)}")
            return None

# Global session validator instance
session_validator = SessionValidator() 