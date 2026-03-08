"""
Cache Manager
Handles caching of LLM responses and analysis results
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheManager:
    """Manages caching of expensive operations"""
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str, max_age_hours: Optional[int] = None) -> Optional[Dict]:
        """
        Retrieve cached data
        
        Args:
            key: Cache key
            max_age_hours: Maximum age in hours (None = no expiry)
        
        Returns:
            Cached data or None if not found/expired
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        if max_age_hours is not None:
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(hours=max_age_hours):
                return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def set(self, key: str, data: Dict):
        """
        Store data in cache
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_or_compute(self, key: str, compute_fn, max_age_hours: Optional[int] = None) -> Dict:
        """
        Get from cache or compute if not found
        
        Args:
            key: Cache key
            compute_fn: Function to compute data if not cached
            max_age_hours: Maximum cache age
        
        Returns:
            Cached or computed data
        """
        cached = self.get(key, max_age_hours)
        
        if cached is not None:
            return cached
        
        data = compute_fn()
        self.set(key, data)
        
        return data
    
    def clear(self):
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }
