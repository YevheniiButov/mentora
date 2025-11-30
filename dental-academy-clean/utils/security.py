"""
Security utilities for Flask application
Provides protection against common attacks and bot scanning
"""

import re
import logging
import os
from flask import request, current_app, abort
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# Setup security-specific logger for security.log file
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

# Prevent duplicate handlers
if not security_logger.handlers:
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    security_logger.addHandler(console_handler)
    
    # File handler for security logs
    try:
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'security.log'),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        security_logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create security.log file handler: {e}")

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
    # Scanner-specific paths
    r'/swagger',
    r'/api-docs',
    r'/swagger-ui',
    r'/v2/api-docs',
    r'/v3/api-docs',
    r'/graphql',
    r'/api/graphql',
    r'/api/gql',
    r'/actuator',
    r'/telescope',
    r'/_all_dbs',
    r'/server-status',
    r'/login\.action',
    r'/\.vscode',
    r'/_catalog',
    r'/debug/default',
    r'/ecp/Current',
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
SCANNER_BLOCK_THRESHOLD = 3  # Block known scanners after 3 requests

# API rate limiting (for /api endpoints)
api_rate_limits = defaultdict(list)
API_RATE_LIMIT = 10  # Max 10 requests per minute to /api
API_RATE_WINDOW = 60  # 1 minute window

# Track blocked IPs for security alerts (Telegram notifications only)
blocked_ips_history = {}
SECURITY_ALERT_THRESHOLD = 10  # Log alert if 10+ IPs blocked in 1 hour (Telegram bot will notify)
last_security_alert_time = None
SECURITY_ALERT_MIN_INTERVAL = 7200  # Minimum 2 hours between security alerts

# Whitelist for legitimate bots and crawlers
LEGITIMATE_BOTS = [
    'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
    'yandexbot', 'facebookexternalhit', 'meta-externalagent',
    'meta-webindexer', 'telegrambot', 'twitterbot', 'linkedinbot',
    'whatsapp', 'applebot', 'chatgpt-user', 'anthropic-ai',
    'claude-web', 'perplexity', 'petalbot', 'sogou', 'exabot',
    'go-http-client',  # Render health checks
]

# Whitelist for SEO and public paths that should always be accessible
SEO_WHITELIST_PATHS = [
    '/robots.txt',
    '/sitemap.xml',
    '/sitemap_index.xml',
    '/sitemap-index.xml',
    '/sitemap.txt',
    '/sitemap.html',
    '/news-sitemap.xml',
    '/news_sitemap.xml',
    '/schema.json',
    '/favicon.ico'
]

def is_legitimate_bot(user_agent=None):
    """
    Check if user agent is a legitimate bot/crawler
    
    Args:
        user_agent: User agent string
        
    Returns:
        bool: True if legitimate bot, False otherwise
    """
    if not user_agent:
        return False
    
    ua_lower = user_agent.lower()
    for bot in LEGITIMATE_BOTS:
        if bot in ua_lower:
            return True
    
    return False

def is_seo_path(path):
    """
    Check if path is an SEO/public path that should always be accessible
    
    Args:
        path: Request path
        
    Returns:
        bool: True if SEO path, False otherwise
    """
    if not path:
        return False
    
    path_lower = path.lower().strip('/')
    for seo_path in SEO_WHITELIST_PATHS:
        if path_lower == seo_path.strip('/') or path_lower.startswith(seo_path.strip('/')):
            return True
    
    return False

def is_known_scanner(user_agent=None):
    """
    Check if user agent is a known security scanner
    
    Args:
        user_agent: User agent string
        
    Returns:
        bool: True if known scanner, False otherwise
    """
    if not user_agent:
        return False
    
    # Don't flag legitimate bots as scanners
    if is_legitimate_bot(user_agent):
        return False
    
    known_scanners = [
        'l9scan', 'leakix', 'sqlmap', 'nikto', 'nmap',
        'masscan', 'zap', 'burp', 'w3af', 'acunetix', 
        'nessus', 'openvas'
    ]
    ua_lower = user_agent.lower()
    for scanner in known_scanners:
        if scanner in ua_lower:
            return True
    
    return False

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
    
    # Never flag static files as suspicious
    if path.startswith('/static/'):
        return False
    
    # Never block SEO/public paths
    if is_seo_path(path):
        return False
    
    path_lower = path.lower()
    
    # Check against suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, path_lower, re.IGNORECASE):
            return True
    
    # If legitimate bot, only block if path is clearly malicious
    if is_legitimate_bot(user_agent):
        # Legitimate bots can access normal paths, only block obvious exploits
        return False
    
    # Check for empty User-Agent - suspicious, but allow for SEO paths
    if not user_agent or user_agent.strip() == '':
        # Empty UA on suspicious paths is bad, but on normal paths might be OK
        # Only flag if path itself is suspicious
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, path_lower, re.IGNORECASE):
                return True
        return False
    
    # Check for suspicious user agents (including scanners)
    if user_agent:
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
            'burp', 'w3af', 'acunetix', 'nessus', 'openvas',
            'l9scan', 'leakix'  # Known security scanners
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
    # Normalize empty user agent
    if not user_agent or user_agent.strip() == '':
        user_agent = '(empty)'
        if reason == 'suspicious_pattern':
            reason = 'empty_user_agent'
    
    # Log to both regular logger and security logger
    log_msg = f"🚨 Suspicious request: IP={ip}, Path={path}, UA={user_agent}, Reason={reason}"
    logger.warning(log_msg)
    security_logger.warning(log_msg)
    
    # Check if this is a known scanner - use more aggressive blocking
    is_scanner = is_known_scanner(user_agent) or (user_agent == '(empty)')
    threshold = SCANNER_BLOCK_THRESHOLD if is_scanner else BLOCK_THRESHOLD
    
    # Track suspicious IP
    suspicious_ips[ip].append({
        'path': path,
        'user_agent': user_agent,
        'reason': reason,
        'timestamp': datetime.now(),
        'is_scanner': is_scanner
    })
    
    # Clean old entries (older than 1 hour)
    cutoff = datetime.now() - timedelta(seconds=BLOCK_DURATION)
    suspicious_ips[ip] = [
        entry for entry in suspicious_ips[ip]
        if entry['timestamp'] > cutoff
    ]
    
    # Check if IP should be blocked
    if len(suspicious_ips[ip]) >= threshold:
        scanner_msg = " (known scanner)" if is_scanner else ""
        block_msg = f"🔒 IP {ip} blocked due to {len(suspicious_ips[ip])} suspicious requests{scanner_msg}"
        logger.error(block_msg)
        security_logger.error(block_msg)
        
        # Track blocked IP for monitoring (Telegram bot will handle notifications)
        blocked_ips_history[ip] = datetime.now()
        # Email alerts disabled - Telegram bot handles notifications automatically
        
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
    
    if not recent_requests:
        return False
    
    # Use scanner threshold if any recent request is from a known scanner
    is_scanner = any(entry.get('is_scanner', False) for entry in recent_requests)
    threshold = SCANNER_BLOCK_THRESHOLD if is_scanner else BLOCK_THRESHOLD
    
    if len(recent_requests) >= threshold:
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
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google.com https://www.gstatic.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "connect-src 'self' https://api.telegram.org https://www.google.com https://cdn.jsdelivr.net https://unpkg.com; "
            "frame-src 'self' https://www.google.com; "
            "frame-ancestors 'none';"
        ),
    }

def check_api_rate_limit(ip):
    """
    Check API rate limit for IP address
    Blocks if more than API_RATE_LIMIT requests per minute to /api endpoints
    Allows authenticated users higher limits
    
    Args:
        ip: Client IP address
        
    Returns:
        bool: True if rate limit exceeded, False otherwise
    """
    try:
        from flask_login import current_user
        
        # Authenticated users get higher limit (30 req/min instead of 10)
        if current_user and current_user.is_authenticated:
            user_limit = 30
        else:
            user_limit = API_RATE_LIMIT
    except:
        user_limit = API_RATE_LIMIT
    
    current_time = time.time()
    
    # Clean old requests
    api_rate_limits[ip] = [
        timestamp for timestamp in api_rate_limits[ip]
        if current_time - timestamp < API_RATE_WINDOW
    ]
    
    # Check rate limit
    if len(api_rate_limits[ip]) >= user_limit:
        security_logger.warning(
            f"🚫 API rate limit exceeded for IP {ip}: "
            f"{len(api_rate_limits[ip])} requests in {API_RATE_WINDOW} seconds (limit: {user_limit})"
        )
        return True
    
    # Add current request
    api_rate_limits[ip].append(current_time)
    return False

def check_and_log_security_alert():
    """
    Check if security alert should be logged (10+ IPs blocked in 1 hour)
    Telegram bot will handle notifications automatically
    Email alerts disabled - using Telegram only
    """
    global last_security_alert_time
    
    try:
        # Clean old blocked IPs (older than 1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        recent_blocked = {
            ip: block_time for ip, block_time in blocked_ips_history.items()
            if block_time > cutoff
        }
        
        # Check if threshold reached
        if len(recent_blocked) >= SECURITY_ALERT_THRESHOLD:
            current_time = datetime.now()
            
            # Check minimum interval between alerts (2 hours)
            if last_security_alert_time is None:
                time_since_last_alert = SECURITY_ALERT_MIN_INTERVAL + 1  # Force first alert
            else:
                time_since_last_alert = (current_time - last_security_alert_time).total_seconds()
            
            # Log to security logger (Telegram bot will pick this up automatically)
            # Email alerts disabled - using Telegram only
            if time_since_last_alert >= SECURITY_ALERT_MIN_INTERVAL:
                blocked_count = len(recent_blocked)
                ips_list = list(recent_blocked.keys())[:20]
                ips_str = ', '.join(ips_list[:10])  # Show first 10 IPs
                if blocked_count > 10:
                    ips_str += f' ... and {blocked_count - 10} more'
                
                alert_msg = (
                    f"🚨 Security Alert: {blocked_count} IPs blocked in last hour\n"
                    f"Blocked IPs: {ips_str}\n"
                    f"Check logs: logs/security.log"
                )
                security_logger.warning(alert_msg)
                logger.warning(alert_msg)
                last_security_alert_time = current_time
    except Exception as e:
        logger.error(f"Error in check_and_log_security_alert: {e}")

# Email alerts disabled - using Telegram bot for notifications only
# The send_security_alert_email function has been removed

def security_middleware():
    """
    Security middleware to check requests before processing
    Should be called in before_request hook
    """
    path = request.path
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Always allow static files - these are safe and shouldn't be blocked
    if path.startswith('/static/'):
        return None
    
    # Always allow admin routes - protected by authentication
    if path.startswith('/admin/'):
        return None
    
    # Always allow language root paths (e.g., /nl, /en) - these are valid routes
    # Check if path is a 2-letter language code at root level
    if len(path) == 3 and path[0] == '/' and path[1:].isalpha():
        return None
    
    # Always allow SEO/public paths - never block these
    if is_seo_path(path):
        return None
    
    # Check legitimate bots - but be more strict if they access suspicious paths
    if is_legitimate_bot(user_agent):
        path_lower = path.lower()
        
        # Check for obvious exploits first
        critical_exploits = [
            r'/\.env', r'/\.git', r'\.php$', r'/\.aws', r'/\.ssh',
            r'/\.htaccess', r'/shell\.php', r'/c99\.php', r'/r57\.php'
        ]
        for pattern in critical_exploits:
            if re.search(pattern, path_lower, re.IGNORECASE):
                # Even legitimate bots shouldn't access exploits
                # If bot tries exploits, it's likely a fake bot
                security_logger.warning(f"🚨 Legitimate bot {user_agent} attempted exploit: {path}")
                # Treat as suspicious request instead of just returning 404
                log_suspicious_request(path, ip, user_agent, reason='fake_bot_exploit')
                abort(404)
        
        # If bot accesses other suspicious patterns, treat as suspicious
        # Real bots don't scan for swagger, api-docs, etc.
        if is_suspicious_request(path, user_agent):
            # This might be a fake bot - log but don't block immediately
            security_logger.warning(f"🚨 Legitimate bot {user_agent} accessed suspicious path: {path}")
            # Return 404 to hide existence, but don't block the bot yet
            abort(404)
        
        return None
    
    # Check if IP is blocked
    if is_ip_blocked(ip):
        security_logger.warning(f"🔒 Blocked request from {ip} to {path}")
        abort(403)
    
    # Check API rate limit for /api endpoints
    if path.startswith('/api'):
        if check_api_rate_limit(ip):
            security_logger.warning(f"🚫 API rate limit exceeded for IP {ip} on {path}")
            abort(429)
    
    # Check if request is suspicious (including empty User-Agent)
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

