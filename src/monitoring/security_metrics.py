from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime, timedelta
from typing import Dict, Set
import time

# Prometheus metrics
failed_logins = Counter(
    'failed_login_attempts_total',
    'Total number of failed login attempts',
    ['ip_address', 'username']
)

rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Total number of rate limit threshold violations',
    ['ip_address', 'endpoint']
)

suspicious_activities = Counter(
    'suspicious_activities_total',
    'Total number of suspicious activities detected',
    ['ip_address', 'activity_type']
)

auth_latency = Histogram(
    'authentication_latency_seconds',
    'Authentication request latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of currently active sessions'
)

blocked_ips = Gauge(
    'blocked_ips_total',
    'Number of currently blocked IP addresses'
)

class SecurityMetricsCollector:
    def __init__(self):
        self.failed_login_tracker: Dict[str, List[datetime]] = {}
        self.rate_limit_tracker: Dict[str, List[datetime]] = {}
        self.suspicious_ip_tracker: Dict[str, Set[str]] = {}
        self._blocked_ips: Set[str] = set()

    def track_failed_login(self, ip_address: str, username: str) -> bool:
        """Track failed login attempts and return True if threshold exceeded"""
        failed_logins.labels(ip_address=ip_address, username=username).inc()
        
        key = f"{ip_address}:{username}"
        now = datetime.utcnow()
        
        # Clean old entries
        if key in self.failed_login_tracker:
            self.failed_login_tracker[key] = [
                t for t in self.failed_login_tracker[key]
                if t > now - timedelta(seconds=monitoring_settings.FAILED_LOGIN_WINDOW)
            ]
        else:
            self.failed_login_tracker[key] = []
            
        self.failed_login_tracker[key].append(now)
        
        return len(self.failed_login_tracker[key]) >= monitoring_settings.FAILED_LOGIN_THRESHOLD

    def track_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Track rate limit violations and return True if threshold exceeded"""
        rate_limit_hits.labels(ip_address=ip_address, endpoint=endpoint).inc()
        
        key = f"{ip_address}:{endpoint}"
        now = datetime.utcnow()
        
        if key in self.rate_limit_tracker:
            self.rate_limit_tracker[key] = [
                t for t in self.rate_limit_tracker[key]
                if t > now - timedelta(seconds=monitoring_settings.RATE_LIMIT_WINDOW)
            ]
        else:
            self.rate_limit_tracker[key] = []
            
        self.rate_limit_tracker[key].append(now)
        
        return len(self.rate_limit_tracker[key]) >= monitoring_settings.RATE_LIMIT_THRESHOLD

    def track_suspicious_activity(self, ip_address: str, activity_type: str) -> bool:
        """Track suspicious activities and return True if threshold exceeded"""
        suspicious_activities.labels(
            ip_address=ip_address,
            activity_type=activity_type
        ).inc()
        
        if ip_address not in self.suspicious_ip_tracker:
            self.suspicious_ip_tracker[ip_address] = set()
            
        self.suspicious_ip_tracker[ip_address].add(activity_type)
        
        return len(self.suspicious_ip_tracker[ip_address]) >= monitoring_settings.SUSPICIOUS_IP_THRESHOLD

    def block_ip(self, ip_address: str):
        """Block an IP address"""
        self._blocked_ips.add(ip_address)
        blocked_ips.set(len(self._blocked_ips))

    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self._blocked_ips.discard(ip_address)
        blocked_ips.set(len(self._blocked_ips))

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if an IP is blocked"""
        return ip_address in self._blocked_ips

metrics_collector = SecurityMetricsCollector() 