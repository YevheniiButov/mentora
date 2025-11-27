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

# Track blocked IPs for email alerts
blocked_ips_history = {}
EMAIL_ALERT_THRESHOLD = 5  # Send email if 5+ IPs blocked in 1 hour
last_email_alert_time = None
EMAIL_ALERT_MIN_INTERVAL = 3600  # Minimum 1 hour between email alerts

# Whitelist for legitimate bots and crawlers
LEGITIMATE_BOTS = [
    'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
    'yandexbot', 'facebookexternalhit', 'meta-externalagent',
    'meta-webindexer', 'telegrambot', 'twitterbot', 'linkedinbot',
    'whatsapp', 'applebot', 'chatgpt-user', 'anthropic-ai',
    'claude-web', 'perplexity', 'petalbot', 'sogou', 'exabot'
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
        
        # Track blocked IP for email alerts
        blocked_ips_history[ip] = datetime.now()
        check_and_send_email_alert()
        
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

def check_and_send_email_alert():
    """
    Check if email alert should be sent (5+ IPs blocked in 1 hour)
    and send email if threshold reached
    """
    global last_email_alert_time
    
    try:
        # Clean old blocked IPs (older than 1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        recent_blocked = {
            ip: block_time for ip, block_time in blocked_ips_history.items()
            if block_time > cutoff
        }
        
        # Check if threshold reached and we haven't sent alert recently
        if len(recent_blocked) >= EMAIL_ALERT_THRESHOLD:
            current_time = datetime.now()
            if last_email_alert_time is None:
                time_since_last = EMAIL_ALERT_MIN_INTERVAL + 1  # Force first alert
            else:
                time_since_last = (current_time - last_email_alert_time).total_seconds()
            
            if time_since_last >= EMAIL_ALERT_MIN_INTERVAL:
                send_security_alert_email(recent_blocked)
                last_email_alert_time = current_time
    except Exception as e:
        logger.error(f"Error in check_and_send_email_alert: {e}")

def send_security_alert_email(blocked_ips_dict):
    """
    Send email alert to admin about multiple IP blockings
    
    Args:
        blocked_ips_dict: Dictionary of blocked IPs and their blocking times
    """
    try:
        from utils.system_monitor import get_admin_email
        from utils.resend_email_service import send_email_via_resend
        
        admin_email = get_admin_email()
        if not admin_email:
            logger.warning("Admin email not configured, skipping security alert")
            return
        
        blocked_count = len(blocked_ips_dict)
        ips_list = list(blocked_ips_dict.keys())[:20]  # Show max 20 IPs
        
        subject = f"🚨 Security Alert: {blocked_count} IPs Blocked"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                .ip-list {{ background: white; padding: 15px; border-radius: 5px; font-family: monospace; }}
                .ip-item {{ padding: 5px; border-bottom: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Security Alert</h1>
                    <p>Multiple IP Addresses Blocked</p>
                </div>
                
                <div class="content">
                    <div class="alert">
                        <strong>⚠️ Attention Required:</strong> {blocked_count} IP addresses have been blocked in the last hour due to suspicious activity.
                    </div>
                    
                    <h2>Blocked IP Addresses:</h2>
                    <div class="ip-list">
                        {'<br>'.join([f'<div class="ip-item">{ip}</div>' for ip in ips_list])}
                        {f'<div class="ip-item">... and {blocked_count - 20} more</div>' if blocked_count > 20 else ''}
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <strong>Action Required:</strong> Review the security logs to ensure these are legitimate threats and not false positives.
                    </p>
                    
                    <p>
                        Check the security logs at: <code>logs/security.log</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_email_via_resend(
            to_email=admin_email,
            subject=subject,
            html_content=html_content,
            from_name="Mentora Security System"
        )
        
        security_logger.info(f"📧 Security alert email sent to {admin_email} about {blocked_count} blocked IPs")
        
    except Exception as e:
        logger.error(f"Failed to send security alert email: {e}")

def security_middleware():
    """
    Security middleware to check requests before processing
    Should be called in before_request hook
    """
    path = request.path
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Always allow SEO/public paths - never block these
    if is_seo_path(path):
        return None
    
    # Always allow legitimate bots on normal paths
    if is_legitimate_bot(user_agent):
        # Only check for obvious exploits, not general suspicious patterns
        path_lower = path.lower()
        critical_exploits = [
            r'/\.env', r'/\.git', r'\.php$', r'/\.aws', r'/\.ssh',
            r'/\.htaccess', r'/shell\.php', r'/c99\.php', r'/r57\.php'
        ]
        for pattern in critical_exploits:
            if re.search(pattern, path_lower, re.IGNORECASE):
                # Even legitimate bots shouldn't access exploits
                security_logger.warning(f"🚨 Legitimate bot {user_agent} attempted exploit: {path}")
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

