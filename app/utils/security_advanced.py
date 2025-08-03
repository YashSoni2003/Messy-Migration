
import secrets

import hmac
from datetime import datetime, timedelta

from typing import Dict, List

class SecurityManager:
    """Advanced security manager with multiple protection layers."""
    
    def __init__(self):
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked due to failed attempts."""
        if ip_address in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False
    
    def record_failed_attempt(self, ip_address: str) -> bool:
        """Record failed login attempt and return if IP should be blocked."""
        now = datetime.now()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []

        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if now - attempt < timedelta(hours=1)
        ]
        
        self.failed_attempts[ip_address].append(now)
        
        if len(self.failed_attempts[ip_address]) >= self.max_attempts:
            self.blocked_ips[ip_address] = now + self.lockout_duration
            return True
        
        return False
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token for form protection."""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, expected: str) -> bool:
        """Validate CSRF token using constant-time comparison."""
        return hmac.compare_digest(token, expected)
    
    def is_safe_redirect_url(self, url: str, allowed_hosts: List[str]) -> bool:
        """Validate redirect URLs to prevent open redirect attacks."""
        if not url:
            return False
        

        if url.startswith('/') and not url.startswith('//'):
            return True

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts
        except Exception:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize uploaded filenames to prevent directory traversal."""
        import re
        # Remove path components and keep only the filename
        filename = filename.split('/')[-1].split('\\')[-1]
        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename[:255]  # Limit length

class InputSanitizer:
    """Advanced input sanitization beyond basic validation."""
    
    @staticmethod
    def sanitize_sql_like_pattern(pattern: str) -> str:
        """Sanitize LIKE patterns to prevent SQL wildcards abuse."""
        return pattern.replace('%', '\\%').replace('_', '\\_')
    
    @staticmethod
    def sanitize_html_content(content: str) -> str:
        """Basic HTML sanitization for user-generated content."""
        import html
        return html.escape(content, quote=True)
    
    @staticmethod
    def validate_json_depth(data: dict, max_depth: int = 10) -> bool:
        """Prevent JSON depth attacks."""
        def _check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                return False
            
            if isinstance(obj, dict):
                return all(_check_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                return all(_check_depth(item, current_depth + 1) for item in obj)
            return True
        
        return _check_depth(data)

security_manager = SecurityManager()
input_sanitizer = InputSanitizer()
