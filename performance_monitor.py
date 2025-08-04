#!/usr/bin/env python3
"""
Performance monitoring for SOC Metrics Analyzer
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.process = psutil.Process()
    
    def start_monitoring(self, operation: str):
        """Start monitoring an operation"""
        self.start_time = time.time()
        self.metrics[operation] = {
            'start_time': datetime.now(),
            'memory_start': self.process.memory_info().rss / 1024 / 1024,  # MB
            'cpu_start': self.process.cpu_percent()
        }
        logger.info(f"Started monitoring: {operation}")
    
    def end_monitoring(self, operation: str) -> Dict[str, Any]:
        """End monitoring and return metrics"""
        if operation not in self.metrics:
            return {}
        
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        memory_end = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_end = self.process.cpu_percent()
        
        metrics = {
            'duration_seconds': duration,
            'memory_peak_mb': max(self.metrics[operation]['memory_start'], memory_end),
            'memory_delta_mb': memory_end - self.metrics[operation]['memory_start'],
            'cpu_peak_percent': max(self.metrics[operation]['cpu_start'], cpu_end),
            'end_time': datetime.now()
        }
        
        self.metrics[operation].update(metrics)
        
        logger.info(f"Completed {operation}: {duration:.2f}s, Memory: {memory_end:.1f}MB")
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        total_duration = sum(m.get('duration_seconds', 0) for m in self.metrics.values())
        total_memory = sum(m.get('memory_peak_mb', 0) for m in self.metrics.values())
        
        return {
            'total_operations': len(self.metrics),
            'total_duration_seconds': total_duration,
            'total_memory_mb': total_memory,
            'operations': self.metrics
        }

def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            monitor.start_monitoring(op_name)
            try:
                result = func(*args, **kwargs)
                monitor.end_monitoring(op_name)
                return result
            except Exception as e:
                logger.error(f"Error in {op_name}: {e}")
                monitor.end_monitoring(op_name)
                raise
        
        return wrapper
    return decorator

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 