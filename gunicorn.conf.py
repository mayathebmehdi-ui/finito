# Gunicorn configuration for production deployment
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 10000)}"
backlog = 2048

# Worker processes
workers = int(os.getenv("WEB_CONCURRENCY", 2))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "ecommerce-analyzer"

# Worker recycling
max_requests = 1000
max_requests_jitter = 50

# Preload app for better performance
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
