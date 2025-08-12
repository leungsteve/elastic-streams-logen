import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import logging

fake = Faker()

class LogGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.correlation_ids = {}
        self.attack_state = {}
        self.business_state = {}
        
    def generate_correlation_id(self, request_type: str = "user") -> str:
        correlation_id = str(uuid.uuid4())
        self.correlation_ids[correlation_id] = {
            'created': datetime.now(),
            'type': request_type
        }
        return correlation_id

class NginxLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.status_codes = {
            200: 0.70, 404: 0.15, 500: 0.05, 403: 0.03, 
            502: 0.02, 301: 0.03, 400: 0.02
        }
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "curl/7.68.0",
            "Go-http-client/1.1",
            "python-requests/2.28.0"
        ]
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        # Check for attack scenario
        is_attack = self._is_attack_request()
        
        if is_attack:
            remote_addr = random.choice(self.config['security']['attack_patterns']['brute_force']['source_ips'])
            status = random.choice([401, 403, 404])
            request_uri = random.choice(["/admin/login", "/wp-admin", "/api/auth/login"])
        else:
            remote_addr = fake.ipv4()
            status = self._weighted_choice(self.status_codes)
            request_uri = random.choice([
                "/", "/products", "/api/users", "/health", "/metrics",
                "/api/orders", "/login", "/checkout", "/search"
            ])
            
        method = "POST" if request_uri in ["/login", "/api/auth/login", "/checkout"] else random.choice(["GET", "POST", "PUT"])
        response_time = random.uniform(0.001, 2.5) if status == 200 else random.uniform(2.0, 10.0)
        bytes_sent = random.randint(200, 50000) if status == 200 else random.randint(100, 1000)
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("http_request")
            
        # Common Log Format
        log_line = (
            f'{remote_addr} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
            f'"{method} {request_uri} HTTP/1.1" {status} {bytes_sent} '
            f'"-" "{random.choice(self.user_agents)}" '
            f'rt={response_time:.3f} correlation_id="{correlation_id}"'
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': log_line,
            'fields': {
                'remote_addr': remote_addr,
                'method': method,
                'request_uri': request_uri,
                'status': status,
                'response_time': response_time,
                'bytes_sent': bytes_sent,
                'correlation_id': correlation_id,
                'host': host_info['name']
            }
        }
    
    def _is_attack_request(self) -> bool:
        if not self.config['security']['attack_patterns']['brute_force']['enabled']:
            return False
        return random.random() < self.config['security']['attack_patterns']['brute_force']['intensity']
    
    def _weighted_choice(self, choices: Dict[int, float]) -> int:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

class JavaAppLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.log_levels = {
            'INFO': 0.60, 'WARN': 0.20, 'ERROR': 0.10, 
            'DEBUG': 0.08, 'TRACE': 0.02
        }
        self.loggers = [
            'com.example.controller.UserController',
            'com.example.service.PaymentService',
            'com.example.repository.OrderRepository',
            'com.example.security.AuthenticationFilter',
            'org.springframework.web.servlet.DispatcherServlet',
            'org.hibernate.SQL'
        ]
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        level = self._weighted_choice(self.log_levels)
        logger = random.choice(self.loggers)
        thread = f"http-nio-8080-exec-{random.randint(1, 20)}"
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("app_request")
            
        message = self._generate_message(level, logger)
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "logger": logger,
            "thread": thread,
            "message": message,
            "correlation_id": correlation_id,
            "host": host_info['name'],
            "service": "user-service",
            "version": "1.2.3"
        }
        
        # Generate raw structured text format for field extraction demo
        exception_text = ""
        if level == "ERROR":
            log_entry["exception"] = {
                "class": "java.sql.SQLException",
                "message": "Connection timeout after 30000ms",
                "stack_trace": "java.sql.SQLException: Connection timeout\\n\\tat com.example.repository.OrderRepository.findById(OrderRepository.java:45)"
            }
            exception_text = f" exception_class=\"java.sql.SQLException\" exception_message=\"Connection timeout after 30000ms\" stack_trace=\"java.sql.SQLException: Connection timeout\\n\\tat com.example.repository.OrderRepository.findById(OrderRepository.java:45)\""
        
        # Raw structured text format requiring field extraction
        raw_log_line = f"{timestamp.isoformat()} [{level:5}] [{thread}] {logger} - {message} correlation_id=\"{correlation_id}\" host=\"{host_info['name']}\" service=\"user-service\" version=\"1.2.3\"{exception_text}"
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': raw_log_line,
            'fields': log_entry
        }
    
    def _generate_message(self, level: str, logger: str) -> str:
        if "Controller" in logger:
            return f"Processing {random.choice(['GET', 'POST', 'PUT'])} request to /api/{random.choice(['users', 'orders', 'payments'])}"
        elif "Service" in logger:
            if level == "ERROR":
                return f"Failed to process payment for order {fake.uuid4()}: Gateway timeout"
            return f"Successfully processed {random.choice(['payment', 'order', 'user registration'])} for user {fake.uuid4()}"
        elif "Repository" in logger:
            return f"Executing query: SELECT * FROM {random.choice(['users', 'orders', 'payments'])} WHERE id = ?"
        elif "Security" in logger:
            return f"User authentication {'successful' if level != 'ERROR' else 'failed'} for user: {fake.user_name()}"
        else:
            return f"Application event: {fake.sentence()}"
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

class KubernetesLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.namespaces = ["default", "kube-system", "monitoring", "app-prod", "app-staging"]
        self.log_levels = {"INFO": 0.70, "WARN": 0.20, "ERROR": 0.10}
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        namespace = random.choice(self.namespaces)
        pod_name = f"{random.choice(['nginx', 'api-server', 'worker', 'redis'])}-{fake.random_int(1000, 9999)}-{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))}"
        container = random.choice(["main", "sidecar", "init"])
        level = self._weighted_choice(self.log_levels)
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("k8s_event")
            
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "namespace": namespace,
            "pod": pod_name,
            "container": container,
            "level": level,
            "message": self._generate_k8s_message(level, namespace),
            "correlation_id": correlation_id,
            "node": host_info['name'],
            "cluster": "production-cluster"
        }
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': json.dumps(log_entry),
            'fields': log_entry
        }
    
    def _generate_k8s_message(self, level: str, namespace: str) -> str:
        if level == "ERROR":
            return random.choice([
                "Pod failed to start: ImagePullBackOff",
                "Container crashed with exit code 1",
                "Failed to mount volume: permission denied",
                "Readiness probe failed: HTTP probe failed with statuscode: 503"
            ])
        elif level == "WARN":
            return random.choice([
                "Pod memory usage above 80%",
                "Container restart count increased",
                "Slow startup detected: 45s to ready",
                "Deprecated API version detected"
            ])
        else:
            return random.choice([
                f"Pod successfully scheduled on node",
                f"Container started successfully",
                f"Health check passed",
                f"Resource limits updated"
            ])
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

class SystemAccessLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.users = ["admin", "deploy", "monitoring", "backup"] + [fake.user_name() for _ in range(10)]
        self.actions = {
            "login": 0.40, "logout": 0.35, "sudo": 0.15, 
            "ssh_key_auth": 0.05, "password_change": 0.05
        }
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        # Check for attack scenario
        is_attack = self._is_attack_attempt()
        
        if is_attack:
            user = random.choice(["admin", "root", "administrator"])
            source_ip = random.choice(self.config['security']['attack_patterns']['brute_force']['source_ips'])
            action = "login"
            result = "FAILED"
            session_id = "none"
        else:
            user = random.choice(self.users)
            source_ip = fake.ipv4()
            action = self._weighted_choice(self.actions)
            result = "SUCCESS" if random.random() > 0.05 else "FAILED"
            session_id = fake.uuid4() if result == "SUCCESS" else "none"
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("access_event")
            
        # Syslog format
        log_line = (
            f'{timestamp.strftime("%b %d %H:%M:%S")} {host_info["name"]} '
            f'sshd[{random.randint(1000, 9999)}]: {result} {action} for user {user} '
            f'from {source_ip} port {random.randint(30000, 65000)} '
            f'session_id="{session_id}" correlation_id="{correlation_id}"'
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': log_line,
            'fields': {
                'user': user,
                'source_ip': source_ip,
                'action': action,
                'result': result,
                'session_id': session_id,
                'correlation_id': correlation_id,
                'host': host_info['name']
            }
        }
    
    def _is_attack_attempt(self) -> bool:
        if not self.config['security']['attack_patterns']['brute_force']['enabled']:
            return False
        return random.random() < self.config['security']['attack_patterns']['brute_force']['intensity']
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

class EcommerceLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.payment_methods = ["credit_card", "paypal", "apple_pay", "google_pay", "bank_transfer"]
        self.status_weights = {"completed": 0.85, "failed": 0.10, "pending": 0.03, "cancelled": 0.02}
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        # Check for payment gateway outage
        is_outage = random.random() < self.config['business']['failure_scenarios']['payment_gateway_outage']['probability']
        
        order_id = fake.uuid4()
        customer_id = fake.uuid4()
        payment_method = random.choice(self.payment_methods)
        amount = round(random.uniform(10.99, 999.99), 2)
        
        if is_outage:
            status = "failed"
            error_code = "GATEWAY_TIMEOUT"
            processing_time = random.uniform(30.0, 60.0)
        else:
            status = self._weighted_choice(self.status_weights)
            error_code = None if status == "completed" else random.choice(["INSUFFICIENT_FUNDS", "CARD_DECLINED", "FRAUD_DETECTED"])
            processing_time = random.uniform(0.5, 5.0)
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("transaction")
            
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": "transaction",
            "order_id": order_id,
            "customer_id": customer_id,
            "payment_method": payment_method,
            "amount": amount,
            "currency": "USD",
            "status": status,
            "processing_time": round(processing_time, 3),
            "correlation_id": correlation_id,
            "host": host_info['name']
        }
        
        if error_code:
            log_entry["error_code"] = error_code
            
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': json.dumps(log_entry),
            'fields': log_entry
        }
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

class APIGatewayLogGenerator(LogGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoints = [
            "/api/v1/auth/login", "/api/v1/users", "/api/v1/orders",
            "/api/v1/payments", "/api/v1/products", "/api/v1/search",
            "/api/v2/analytics", "/api/v1/health"
        ]
        self.client_types = ["mobile_app", "web_app", "partner_api", "internal_service"]
        
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        # Check for API abuse
        is_abuse = random.random() < self.config['security']['attack_patterns']['api_abuse']['intensity']
        
        if is_abuse:
            endpoint = random.choice(self.config['security']['attack_patterns']['api_abuse']['target_endpoints'])
            api_key = "suspicious_key_" + fake.uuid4()[:8]
            rate_limit_exceeded = True
            response_code = 429
        else:
            endpoint = random.choice(self.endpoints)
            api_key = fake.uuid4()
            rate_limit_exceeded = False
            response_code = random.choices([200, 201, 400, 401, 404, 500], weights=[70, 10, 8, 5, 4, 3])[0]
            
        client_id = fake.uuid4()
        response_time = random.uniform(10, 500)  # milliseconds
        quota_remaining = random.randint(0, 1000) if not rate_limit_exceeded else 0
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("api_request")
            
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "endpoint": endpoint,
            "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
            "api_key": api_key,
            "client_id": client_id,
            "client_type": random.choice(self.client_types),
            "response_code": response_code,
            "response_time": round(response_time, 2),
            "rate_limit_exceeded": rate_limit_exceeded,
            "quota_remaining": quota_remaining,
            "correlation_id": correlation_id,
            "host": host_info['name']
        }
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': json.dumps(log_entry),
            'fields': log_entry
        }

# Additional generators would follow similar patterns...
# For brevity, I'll create placeholder classes for the remaining log types

class DatabaseLogGenerator(LogGenerator):
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        # Check for database slowdown scenario
        is_slow = random.random() < self.config['business']['failure_scenarios']['database_slowdown']['probability']
        slowdown_factor = self.config['business']['failure_scenarios']['database_slowdown']['slowdown_factor'] if is_slow else 1
        
        query_types = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        tables = ["users", "orders", "products", "payments", "sessions"]
        
        query_type = random.choice(query_types)
        table = random.choice(tables)
        duration = random.uniform(0.001, 1.0) * slowdown_factor
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("db_query")
        
        # PostgreSQL log format
        log_line = (
            f'{timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]} UTC '
            f'[{random.randint(1000, 9999)}] LOG: duration: {duration*1000:.3f} ms '
            f'statement: {query_type} * FROM {table} WHERE id = $1 '
            f'correlation_id="{correlation_id}"'
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': log_line,
            'fields': {
                'query_type': query_type,
                'table_name': table,
                'duration': round(duration, 6),
                'correlation_id': correlation_id,
                'host': host_info['name']
            }
        }

class DockerLogGenerator(LogGenerator):
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        container_events = ["start", "stop", "restart", "oom_kill", "health_check"]
        event = random.choice(container_events)
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("container_event")
            
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "container_id": fake.uuid4()[:12],
            "image": f"{random.choice(['nginx', 'postgres', 'redis', 'app'])}:{fake.random_int(1, 5)}.{fake.random_int(0, 9)}",
            "event": event,
            "exit_code": random.choice([0, 1, 125, 137]) if event in ["stop", "oom_kill"] else None,
            "correlation_id": correlation_id,
            "host": host_info['name']
        }
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': json.dumps(log_entry),
            'fields': log_entry
        }

class CDNLogGenerator(LogGenerator):
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("cdn_request")
            
        cache_status = random.choices(["HIT", "MISS", "STALE"], weights=[70, 25, 5])[0]
        edge_location = random.choice(["us-west-1", "us-east-1", "eu-west-1", "ap-southeast-1"])
        
        log_line = (
            f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")} {edge_location} '
            f'{fake.ipv4()} {random.choice(["GET", "POST"])} '
            f'/static/{fake.file_name()} {random.choice([200, 304, 404, 502])} '
            f'{cache_status} {random.randint(100, 50000)} '
            f'correlation_id="{correlation_id}"'
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': log_line,
            'fields': {
                'edge_location': edge_location,
                'cache_status': cache_status,
                'correlation_id': correlation_id,
                'host': host_info['name']
            }
        }

class CICDLogGenerator(LogGenerator):
    def generate_log(self, host_info: Dict[str, Any], correlation_id: str = None) -> Dict[str, str]:
        timestamp = datetime.now()
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id("build_event")
            
        stages = ["build", "test", "security_scan", "deploy"]
        stage = random.choice(stages)
        status = random.choices(["success", "failure"], weights=[85, 15])[0]
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "build_id": fake.uuid4(),
            "stage": stage,
            "status": status,
            "duration": random.randint(30, 600),
            "commit_hash": fake.sha1(),
            "branch": random.choice(["main", "develop", "feature/auth", "hotfix/payment"]),
            "correlation_id": correlation_id,
            "host": host_info['name']
        }
        
        return {
            'timestamp': timestamp.isoformat(),
            'log_line': json.dumps(log_entry),
            'fields': log_entry
        }