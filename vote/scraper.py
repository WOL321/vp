"""
Enhanced vote scraper with advanced error handling, retry logic, and analytics
"""

import re
import asyncio
import aiohttp
import cloudscraper
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import logging

from config import VOTE_SITES, SCRAPE_INTERVAL_SECONDS
from core.data_manager import data_manager

logger = logging.getLogger("Nariño")

class AdvancedVoteScraper:
    """Advanced vote scraper with multiple strategies and analytics"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_successful_counts = {}
        self.scrape_attempts = {}
        self.consecutive_failures = {}
        self.scrape_history = []  # Track all scrape attempts
        self.site_health = {}  # Track site health metrics
        
        # Initialize tracking
        for site in VOTE_SITES:
            name = site["name"]
            self.scrape_attempts[name] = {"success": 0, "fail": 0, "playwright": 0}
            self.consecutive_failures[name] = 0
            self.site_health[name] = {
                "uptime": 100.0,
                "avg_response_time": 0,
                "last_success": None,
                "total_scrapes": 0,
                "successful_scrapes": 0
            }
    
    async def start(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def _validate_vote_count(self, name: str, count: int, previous: Optional[int] = None) -> bool:
        """Validate vote count with advanced checks"""
        if count < 0:
            logger.warning(f"{name}: Invalid vote count {count} (negative)")
            return False
        
        if count > 1000000:
            logger.warning(f"{name}: Suspicious vote count {count} (too large)")
            return False
        
        # Check for suspicious jumps
        if previous is not None:
            diff = abs(count - previous)
            if diff > 100:
                logger.warning(f"{name}: Suspicious vote jump: {previous} -> {count} (diff: {diff})")
        
        return True
    
    def _extract_with_beautifulsoup(self, html: str, site_name: str) -> Optional[int]:
        """Extract vote count using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Minecraft-MP
            if site_name == "Minecraft-MP":
                for row in soup.find_all('tr'):
                    strong_tag = row.find('strong')
                    if strong_tag and 'Vote(s)' in strong_tag.get_text():
                        tds = row.find_all('td')
                        if len(tds) >= 2:
                            vote_text = tds[1].get_text().strip()
                            match = re.search(r'(\d+)', vote_text)
                            if match:
                                return int(match.group(1))
            
            # MinecraftServers.org
            elif site_name == "MinecraftServers.org":
                for row in soup.find_all('div', class_='row'):
                    cols = row.find_all('div', recursive=False)
                    if len(cols) >= 2:
                        label = cols[0].get_text().strip()
                        if label == "Votes":
                            vote_text = cols[1].get_text().strip()
                            match = re.search(r'(\d+)', vote_text)
                            if match:
                                return int(match.group(1))
            
            # Minecraft-Server-List
            elif site_name == "Minecraft-Server-List":
                text = soup.get_text()
                match = re.search(r'(\d+)\s+Players have voted', text)
                if match:
                    return int(match.group(1))
                
                match = re.search(r'<b>(\d+)\s+Votes\s*-\s*All time</b>', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"{site_name}: BeautifulSoup extraction error - {e}")
            return None
    
    def _extract_with_regex(self, html: str, site: dict) -> Optional[int]:
        """Extract vote count using regex patterns"""
        for pattern in site.get("fallback_patterns", []):
            try:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    return int(match.group(1))
            except Exception as e:
                logger.debug(f"{site['name']}: Regex pattern failed - {e}")
                continue
        return None
    
    async def scrape_site(self, site: dict, max_retries: int = 3) -> Tuple[str, Optional[int]]:
        """Scrape a single site with advanced retry logic"""
        name = site["name"]
        url = site["url"]
        start_time = datetime.now()
        
        # Update health tracking
        self.site_health[name]["total_scrapes"] += 1
        
        for attempt in range(max_retries + 1):
            try:
                # Get HTML content
                if name == "Minecraft-Server-List":
                    html = await self._fetch_with_cloudscraper(url, name)
                else:
                    html = await self._fetch_with_aiohttp(url, name)
                
                if not html:
                    if attempt < max_retries:
                        wait_time = min(2 ** attempt, 10)
                        logger.info(f"{name}: Retry {attempt + 1}/{max_retries} (waiting {wait_time}s)")
                        await asyncio.sleep(wait_time)
                        continue
                    return self._get_cached_or_none(name)
                
                # Strategy 1: BeautifulSoup
                count = self._extract_with_beautifulsoup(html, name)
                if count is not None and self._validate_vote_count(name, count, self.last_successful_counts.get(name)):
                    logger.info(f"{name}: Found {count} votes (BeautifulSoup)")
                    self._record_success(name, count)
                    return name, count
                
                # Strategy 2: Regex
                count = self._extract_with_regex(html, site)
                if count is not None and self._validate_vote_count(name, count, self.last_successful_counts.get(name)):
                    logger.info(f"{name}: Found {count} votes (Regex)")
                    self._record_success(name, count)
                    return name, count
                
                # Both strategies failed
                logger.warning(f"{name}: Could not extract vote count (attempt {attempt + 1}/{max_retries + 1})")
                
                if attempt < max_retries:
                    wait_time = min(2 ** attempt, 10)
                    await asyncio.sleep(wait_time)
                    continue
                
                # All attempts failed
                self._record_failure(name)
                return self._get_cached_or_none(name)
            
            except Exception as e:
                logger.error(f"{name}: Scrape error (attempt {attempt + 1}/{max_retries + 1}) - {e}")
                if attempt < max_retries:
                    wait_time = min(2 ** attempt, 10)
                    await asyncio.sleep(wait_time)
                    continue
                self._record_failure(name)
                return self._get_cached_or_none(name)
    
    def _record_success(self, name: str, count: int):
        """Record successful scrape"""
        self.last_successful_counts[name] = count
        self.scrape_attempts[name]["success"] += 1
        self.consecutive_failures[name] = 0
        self.site_health[name]["successful_scrapes"] += 1
        self.site_health[name]["last_success"] = datetime.now().isoformat()
        
        # Calculate uptime
        total = self.site_health[name]["total_scrapes"]
        successful = self.site_health[name]["successful_scrapes"]
        self.site_health[name]["uptime"] = (successful / total * 100) if total > 0 else 100.0
        
        # Record in history
        self.scrape_history.append({
            "timestamp": datetime.now().isoformat(),
            "site": name,
            "success": True,
            "count": count
        })
        
        # Keep only last 1000 entries
        if len(self.scrape_history) > 1000:
            self.scrape_history = self.scrape_history[-1000:]
    
    def _record_failure(self, name: str):
        """Record failed scrape"""
        self.scrape_attempts[name]["fail"] += 1
        self.consecutive_failures[name] += 1
        
        # Record in history
        self.scrape_history.append({
            "timestamp": datetime.now().isoformat(),
            "site": name,
            "success": False,
            "count": None
        })
        
        # Keep only last 1000 entries
        if len(self.scrape_history) > 1000:
            self.scrape_history = self.scrape_history[-1000:]
    
    async def _fetch_with_cloudscraper(self, url: str, name: str) -> Optional[str]:
        """Fetch HTML using cloudscraper"""
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=20)
            
            if response.status_code != 200:
                logger.warning(f"{name}: HTTP {response.status_code}")
                return None
            
            return response.text
        except Exception as e:
            logger.error(f"{name}: Cloudscraper error - {e}")
            return None
    
    async def _fetch_with_aiohttp(self, url: str, name: str) -> Optional[str]:
        """Fetch HTML using aiohttp"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    return None
                return await resp.text()
        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            return None
        except Exception as e:
            logger.error(f"{name}: Fetch error - {e}")
            return None
    
    def _get_cached_or_none(self, name: str) -> Tuple[str, Optional[int]]:
        """Return cached value or None"""
        if name in self.last_successful_counts:
            logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
            return name, self.last_successful_counts[name]
        logger.warning(f"{name}: No cached value available")
        return name, None
    
    async def scrape_all(self) -> Tuple[Dict[str, Optional[int]], int]:
        """Scrape all sites and return counts"""
        counts = {}
        total = 0
        
        for i, site in enumerate(VOTE_SITES):
            name, count = await self.scrape_site(site)
            counts[name] = count
            if count is not None:
                total += count
            
            if i < len(VOTE_SITES) - 1:
                await asyncio.sleep(1)
        
        logger.info(f"Scrape complete: {counts} | Total: {total}")
        return counts, total
    
    def get_stats(self) -> dict:
        """Get scraper statistics"""
        return {
            "last_successful_counts": self.last_successful_counts.copy(),
            "scrape_attempts": self.scrape_attempts.copy(),
            "consecutive_failures": self.consecutive_failures.copy(),
            "site_health": self.site_health.copy(),
            "recent_history": self.scrape_history[-10:] if self.scrape_history else []
        }
    
    def get_site_health(self, name: str) -> dict:
        """Get health metrics for a specific site"""
        return self.site_health.get(name, {})
    
    def get_voting_rate(self, history: list) -> Optional[float]:
        """Calculate current voting rate in votes per hour"""
        if len(history) < 2:
            return None
        
        recent = history[-10:]
        if len(recent) < 2:
            return None
        
        first_time = recent[0]["timestamp"]
        first_votes = recent[0]["total"]
        last_time = recent[-1]["timestamp"]
        last_votes = recent[-1]["total"]
        
        time_diff_hours = (last_time - first_time) / 3600
        vote_diff = last_votes - first_votes
        
        if time_diff_hours <= 0 or vote_diff <= 0:
            return None
        
        return vote_diff / time_diff_hours
    
    def estimate_completion(self, history: list, remaining: int) -> Optional[str]:
        """Estimate time to completion"""
        if len(history) < 2:
            return None
        
        recent = history[-10:]
        if len(recent) < 2:
            return None
        
        first_time = recent[0]["timestamp"]
        first_votes = recent[0]["total"]
        last_time = recent[-1]["timestamp"]
        last_votes = recent[-1]["total"]
        
        time_diff = last_time - first_time
        vote_diff = last_votes - first_votes
        
        if time_diff <= 0 or vote_diff <= 0:
            return None
        
        votes_per_second = vote_diff / time_diff
        seconds_to_complete = remaining / votes_per_second
        
        if seconds_to_complete < 60:
            return f"~{int(seconds_to_complete)}s"
        elif seconds_to_complete < 3600:
            return f"~{int(seconds_to_complete / 60)}m"
        else:
            return f"~{seconds_to_complete / 3600:.1f}h"
