"""
Gunicorn configuration file for production deployment
"""

import os
import multiprocessing

# Bind address
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker settings
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'
threads = int(os.getenv('GUNICORN_THREADS', '2'))
worker_connections = 1000

# Timeouts
timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
proc_name = 'lol-analytics'

# Preload app for better performance and lower memory per worker
preload_app = True

# Maximum requests before worker restart (helps prevent memory leaks)
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '100'))

# Hooks
def on_starting(server):
    server.log.info("Starting LoL Analytics Agent")

def when_ready(server):
    server.log.info("LoL Analytics Agent is ready to accept connections")

def on_exit(server):
    server.log.info("Shutting down LoL Analytics Agent")
