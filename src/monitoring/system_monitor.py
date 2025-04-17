from typing import Dict, Any
import asyncio
import psutil
import prometheus_client as prom
from datetime import datetime
import logging

class SystemMonitor:
    def __init__(self):
        # Prometheus metrics
        self.request_counter = prom.Counter(
            'request_total',
            'Total requests processed',
            ['endpoint', 'method', 'status']
        )
        self.response_time = prom.Histogram(
            'response_time_seconds',
            'Response time in seconds',
            ['endpoint']
        )
        self.memory_gauge = prom.Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        self.active_users = prom.Gauge(
            'active_users',
            'Number of active users'
        )
        
    async def start_monitoring(self):
        """Start all monitoring tasks"""
        await asyncio.gather(
            self.monitor_system_metrics(),
            self.monitor_application_metrics(),
            self.monitor_security_metrics(),
            self.monitor_business_metrics()
        )
        
    async def monitor_system_metrics(self):
        """Monitor system-level metrics"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric('cpu_usage', cpu_percent)
                
                # Memory usage
                memory = psutil.Process().memory_info()
                self.memory_gauge.set(memory.rss)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.record_metric('disk_usage', disk.percent)
                
                # Network stats
                network = psutil.net_io_counters()
                self.record_metric('network_bytes_sent', network.bytes_sent)
                self.record_metric('network_bytes_recv', network.bytes_recv)
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Error monitoring system metrics: {str(e)}")
                
    async def monitor_application_metrics(self):
        """Monitor application-specific metrics"""
        while True:
            try:
                # Active sessions
                active_sessions = len(self.get_active_sessions())
                self.active_users.set(active_sessions)
                
                # Response times
                response_times = self.get_response_times()
                for endpoint, time in response_times.items():
                    self.response_time.labels(endpoint=endpoint).observe(time)
                    
                # Error rates
                error_rates = self.get_error_rates()
                for endpoint, rate in error_rates.items():
                    self.record_metric(f'error_rate_{endpoint}', rate)
                    
                await asyncio.sleep(30)
                
            except Exception as e:
                logging.error(f"Error monitoring application metrics: {str(e)}") 