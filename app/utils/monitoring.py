
import time
import json
from datetime import datetime
from collections import defaultdict, deque
from threading import Lock
from functools import wraps

class MetricsCollector:
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(deque)
        self.error_counts = defaultdict(int)
        self.active_connections = 0
        self.total_requests = 0
        self.lock = Lock()
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        with self.lock:
            key = f"{method} {endpoint}"
            self.request_counts[key] += 1
            self.total_requests += 1
            
            # Keep only last 100 response times for each endpoint
            times = self.response_times[key]
            times.append(response_time)
            if len(times) > 100:
                times.popleft()
            
            if status_code >= 400:
                self.error_counts[key] += 1
    
    def get_metrics_summary(self) -> dict:
        with self.lock:
            summary = {
                'total_requests': self.total_requests,
                'active_connections': self.active_connections,
                'timestamp': datetime.utcnow().isoformat(),
                'endpoints': {}
            }
            
            for endpoint, count in self.request_counts.items():
                times = list(self.response_times[endpoint])
                error_count = self.error_counts.get(endpoint, 0)
                
                summary['endpoints'][endpoint] = {
                    'request_count': count,
                    'error_count': error_count,
                    'error_rate': error_count / count if count > 0 else 0,
                    'avg_response_time': sum(times) / len(times) if times else 0,
                    'max_response_time': max(times) if times else 0
                }
            
            return summary

def monitor_performance(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            response_time = time.time() - start_time
            
     
            status_code = 200
            if isinstance(result, tuple) and len(result) > 1:
                status_code = result[1]
            
       
            metrics_collector.record_request(
                endpoint=f.__name__,
                method='HTTP',
                status_code=status_code,
                response_time=response_time
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            metrics_collector.record_request(
                endpoint=f.__name__,
                method='HTTP',
                status_code=500,
                response_time=response_time
            )
            raise
    
    return decorated_function

class HealthChecker:
    """Application health monitoring."""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def run_health_checks(self) -> dict:
        """Run all registered health checks."""
        results = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][name] = {
                    'status': 'healthy',
                    'details': check_result
                }
            except Exception as e:
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                overall_healthy = False
        
        if not overall_healthy:
            results['status'] = 'unhealthy'
        
        return results


metrics_collector = MetricsCollector()
health_checker = HealthChecker()


def check_database_connection():
    """Check if database is accessible."""
    from app.utils.database import db_manager
    try:
        db_manager.execute_query("SELECT 1")
        return {"connection": "ok"}
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")

def check_memory_usage():
    """Check memory usage."""
    import psutil
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        raise Exception(f"High memory usage: {memory.percent}%")
    return {"memory_percent": memory.percent}

health_checker.register_check('database', check_database_connection)
health_checker.register_check('memory', check_memory_usage)
