"""
Security utilities for Flask application
Provides protection against common attacks and bot scanning
"""

import re
import logging
from flask import request, current_app, abort
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# Suspicious patterns to block
SUSPICIOUS_PATTERNS = [
    # PHP file scanning
    r'\.php$',
    r'\.php\?',
    r'wp-admin',
    r'wp-content',
    r'wp-includes',
    r'wp-login',
    r'wp-config',
    r'filemanager',
    r'admin\.php',
    r'function\.php',
    r'install\.php',
    r'security\.php',
    r'manager\.php',
    r'\.well-known/admin',
    r'\.well-known/log',
    # Common exploit paths
    r'/\.env',
    r'/\.git',
    r'/\.htaccess',
    r'/\.aws',
    r'/\.ssh',
    r'/backup',
    r'/config\.php',
    r'/database\.php',
    r'/shell\.php',
    r'/c99\.php',
    r'/r57\.php',
    # SQL injection patterns
    r'union.*select',
    r'select.*from',
    r'insert.*into',
    r'delete.*from',
    r'drop.*table',
    r'exec.*\(',
    r'script.*>',
    # XSS patterns
    r'<script',
    r'javascript:',
    r'onerror=',
    r'onload=',
    r'eval\(',
]

# Track suspicious IPs
suspicious_ips = defaultdict(list)
BLOCK_THRESHOLD = 10  # Block after 10 suspicious requests
BLOCK_DURATION = 3600  # Block for 1 hour

def is_suspicious_request(path, user_agent=None):
    """
    Check if request path matches suspicious patterns
    
    Args:
        path: Request path
        user_agent: User agent string
        
    Returns:
        bool: True if suspicious, False otherwise
    """
    if not path:
        return False
    
    path_lower = path.lower()
    
    # Check against suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, path_lower, re.IGNORECASE):
            return True
    
    # Check for suspicious user agents
    if user_agent:
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
            'burp', 'w3af', 'acunetix', 'nessus', 'openvas'
        ]
        ua_lower = user_agent.lower()
        for agent in suspicious_agents:
            if agent in ua_lower:
                return True
    
    return False

def log_suspicious_request(path, ip, user_agent, reason='suspicious_pattern'):
    """
    Log suspicious request for monitoring
    
    Args:
        path: Request path
        ip: Client IP address
        user_agent: User agent string
        reason: Reason for flagging as suspicious
    """
    logger.warning(
        f"🚨 Suspicious request detected: "
        f"IP={ip}, Path={path}, UA={user_agent}, Reason={reason}"
    )
    
    # Track suspicious IP
    suspicious_ips[ip].append({
        'path': path,
        'user_agent': user_agent,
        'reason': reason,
        'timestamp': datetime.now()
    })
    
    # Clean old entries (older than 1 hour)
    cutoff = datetime.now() - timedelta(seconds=BLOCK_DURATION)
    suspicious_ips[ip] = [
        entry for entry in suspicious_ips[ip]
        if entry['timestamp'] > cutoff
    ]
    
    # Check if IP should be blocked
    if len(suspicious_ips[ip]) >= BLOCK_THRESHOLD:
        logger.error(f"🔒 IP {ip} blocked due to {len(suspicious_ips[ip])} suspicious requests")
        return True
    
    return False

def is_ip_blocked(ip):
    """
    Check if IP is currently blocked
    
    Args:
        ip: Client IP address
        
    Returns:
        bool: True if blocked, False otherwise
    """
    if ip not in suspicious_ips:
        return False
    
    # Check if IP has exceeded threshold
    cutoff = datetime.now() - timedelta(seconds=BLOCK_DURATION)
    recent_requests = [
        entry for entry in suspicious_ips[ip]
        if entry['timestamp'] > cutoff
    ]
    
    if len(recent_requests) >= BLOCK_THRESHOLD:
        return True
    
    return False

def get_security_headers():
    """
    Get security headers for responses
    
    Returns:
        dict: Security headers
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        # Content Security Policy
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google.com https://www.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "connect-src 'self' https://api.telegram.org https://www.google.com; "
            "frame-src 'self' https://www.google.com; "
            "frame-ancestors 'none';"
        ),
    }

def security_middleware():
    """
    Security middleware to check requests before processing
    Should be called in before_request hook
    """
    path = request.path
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Check if IP is blocked
    if is_ip_blocked(ip):
        logger.warning(f"🔒 Blocked request from {ip} to {path}")
        abort(403)
    
    # Check if request is suspicious
    if is_suspicious_request(path, user_agent):
        should_block = log_suspicious_request(path, ip, user_agent)
        if should_block:
            abort(403)
        # For suspicious but not yet blocked, return 404 to hide existence
        abort(404)
    
    return None

def rate_limit_by_ip(max_requests=100, window=60):
    """
    Rate limiting decorator based on IP address
    
    Args:
        max_requests: Maximum requests per window
        window: Time window in seconds
    """
    request_counts = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            # Clean old requests
            request_counts[ip] = [
                timestamp for timestamp in request_counts[ip]
                if current_time - timestamp < window
            ]
            
            # Check rate limit
            if len(request_counts[ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP {ip}: {len(request_counts[ip])} requests")
                abort(429)
            
            # Add current request
            request_counts[ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_blocked_ips():
    """
    Get list of currently blocked IPs
    
    Returns:
        list: List of blocked IP addresses
    """
    blocked = []
    cutoff = datetime.now() - timedelta(seconds=BLOCK_DURATION)
    
    for ip, requests in suspicious_ips.items():
        recent = [r for r in requests if r['timestamp'] > cutoff]
        if len(recent) >= BLOCK_THRESHOLD:
            blocked.append({
                'ip': ip,
                'requests_count': len(recent),
                'blocked_until': (cutoff + timedelta(seconds=BLOCK_DURATION)).isoformat()
            })
    
    return blocked

def unblock_ip(ip):
    """
    Manually unblock an IP address
    
    Args:
        ip: IP address to unblock
    """
    if ip in suspicious_ips:
        del suspicious_ips[ip]
        logger.info(f"IP {ip} manually unblocked")

