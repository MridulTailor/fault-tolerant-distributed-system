import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
NODE_MANAGER_URL = os.getenv("NODE_MANAGER_URL", "http://node-manager:8002")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://scheduler_user:scheduler_password@postgres:5432/scheduler_db")
