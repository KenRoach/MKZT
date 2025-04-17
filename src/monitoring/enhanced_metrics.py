from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict
import time

# Order Metrics
order_processing_time = Histogram(
    'order_processing_seconds',
    'Time taken to process orders',
    ['order_type', 'status'],
    buckets=[10, 30, 60, 120, 300, 600]
)

order_items = Counter(
    'order_items_total',
    'Number of items ordered',
    ['item 