from datetime import datetime

class CircuitBreaker:
    def __init__(self, threshold: int = 4, timeout: int = 30):
        self.failure_count: int = 0
        self.state: str = "CLOSED"  # Possible states: CLOSED, OPEN, HALF-OPEN
        self.last_opened: datetime = None
        self.threshold = threshold
        self.timeout = timeout
    
    def record_failure(self):
        self.failure_count += 1
        if self.state == "HALF-OPEN":
            self.state = "OPEN"
            self.last_opened = datetime.now()
        elif self.failure_count >= self.threshold:
            self.state = "OPEN"
            self.last_opened = datetime.now()
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def reset(self):
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_opened = None
    
    def allow_request(self) -> bool:
        if self.state == "OPEN":
            if (datetime.now() - self.last_opened).total_seconds() > self.timeout:
                self.state = "HALF-OPEN"
                return True
            return False
        return True