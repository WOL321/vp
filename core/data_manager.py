"""
Advanced data manager with SQLite-like JSON storage and caching
"""

import json
import os
from typing import Any, Optional, Dict, List
from datetime import datetime
import asyncio

class DataManager:
    """Advanced data persistence with caching and auto-save"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.cache = {}
        self.dirty = set()  # Track which files need saving
        self._save_task = None
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        
        # Start auto-save task
        self._start_auto_save()
    
    def _start_auto_save(self):
        """Start background auto-save task"""
        async def auto_save():
            while True:
                await asyncio.sleep(30)  # Save every 30 seconds
                await self.save_all()
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._save_task = asyncio.create_task(auto_save())
        except RuntimeError:
            pass  # No event loop yet
    
    async def save_all(self):
        """Save all dirty files"""
        for file_key in list(self.dirty):
            await self._save_file(file_key)
        self.dirty.clear()
    
    async def _save_file(self, file_key: str):
        """Save a specific file"""
        if file_key in self.cache:
            file_path = os.path.join(self.data_dir, f"{file_key}.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.cache[file_key], f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving {file_key}: {e}")
    
    def load(self, file_key: str, default: Any = None) -> Any:
        """Load data from file with caching"""
        if file_key in self.cache:
            return self.cache[file_key]
        
        file_path = os.path.join(self.data_dir, f"{file_key}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache[file_key] = data
                    return data
            except Exception as e:
                print(f"Error loading {file_key}: {e}")
        
        # Return default and cache it
        self.cache[file_key] = default if default is not None else {}
        return self.cache[file_key]
    
    def save(self, file_key: str, data: Any):
        """Save data to cache and mark as dirty"""
        self.cache[file_key] = data
        self.dirty.add(file_key)
    
    def get(self, file_key: str, key: str, default: Any = None) -> Any:
        """Get a value from a file"""
        data = self.load(file_key, {})
        return data.get(key, default)
    
    def set(self, file_key: str, key: str, value: Any):
        """Set a value in a file"""
        data = self.load(file_key, {})
        data[key] = value
        self.save(file_key, data)
    
    def delete(self, file_key: str, key: str):
        """Delete a key from a file"""
        data = self.load(file_key, {})
        if key in data:
            del data[key]
            self.save(file_key, data)
    
    def append(self, file_key: str, key: str, value: Any):
        """Append to a list in a file"""
        data = self.load(file_key, {})
        if key not in data:
            data[key] = []
        data[key].append(value)
        self.save(file_key, data)
    
    def increment(self, file_key: str, key: str, amount: int = 1):
        """Increment a numeric value"""
        data = self.load(file_key, {})
        data[key] = data.get(key, 0) + amount
        self.save(file_key, data)
    
    def decrement(self, file_key: str, key: str, amount: int = 1):
        """Decrement a numeric value"""
        data = self.load(file_key, {})
        data[key] = max(0, data.get(key, 0) - amount)
        self.save(file_key, data)
    
    def exists(self, file_key: str, key: str = None) -> bool:
        """Check if a file or key exists"""
        if key is None:
            return file_key in self.cache or os.path.exists(os.path.join(self.data_dir, f"{file_key}.json"))
        
        data = self.load(file_key, {})
        return key in data
    
    def clear(self, file_key: str):
        """Clear a file"""
        self.cache[file_key] = {}
        self.dirty.add(file_key)
    
    def get_all_keys(self, file_key: str) -> List[str]:
        """Get all keys in a file"""
        data = self.load(file_key, {})
        return list(data.keys())
    
    def search(self, file_key: str, predicate) -> List[Any]:
        """Search for items matching a predicate"""
        data = self.load(file_key, {})
        return [item for item in data.values() if predicate(item)]

# Global instance
data_manager = DataManager()
