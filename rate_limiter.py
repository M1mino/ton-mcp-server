"""Rate limiter для free tier"""
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.daily = defaultdict(int)
        self.minute = defaultdict(list)
        self._last_reset = time.time()
    
    def check(self, api_key: str, daily_limit: int = 100, rate_per_minute: int = 10) -> dict:
        now = time.time()
        
        # Reset daily every 24h
        if now - self._last_reset > 86400:
            self.daily.clear()
            self._last_reset = now
        
        # Daily check
        if self.daily[api_key] >= daily_limit:
            return {"allowed": False, "reason": "Daily limit exceeded"}
        
        # Rate per minute check
        self.minute[api_key] = [t for t in self.minute[api_key] if now - t < 60]
        if len(self.minute[api_key]) >= rate_per_minute:
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        self.daily[api_key] += 1
        self.minute[api_key].append(now)
        
        return {
            "allowed": True,
            "daily_used": self.daily[api_key],
            "daily_left": daily_limit - self.daily[api_key],
        }
