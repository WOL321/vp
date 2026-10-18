"""
Enhanced web scraper for vote count sites with multiple extraction strategies.
"""

import re
import asyncio
import logging
from typing import Optional
import aiohttp
import cloudscraper
from bs4 import BeautifulSoup
from config import VOTE_SITES

logger = logging.getLogger("VotePartyBot")


class VoteScraper:
    """
    Scrapes vote counts from Minecraft server list websites.
    Uses multiple extraction strategies for maximum reliability:
    1. BeautifulSoup CSS selectors (most reliable)
    2. Regex patterns (fallback)
    3. Multiple retry attempts
    4. Data validation
    5. Caching to prevent data loss
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_successful_counts: dict[str, int] = {}
        self.scrape_attempts: dict[str, int] = {}  # Track success rate

    async def start(self):
        """Initialize the HTTP session with proper headers."""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        )

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

    def _validate_vote_count(self, name: str, count: int, previous: Optional[int] = None) -> bool:
        """
        Validate that a vote count is reasonable.
        Checks for:
        - Positive numbers
        - Not too large (< 1M)
        - Not too different from previous (if available)
        """
        if count < 0:
            logger.warning(f"{name}: Invalid vote count {count} (negative)")
            return False
        
        if count > 1000000:
            logger.warning(f"{name}: Suspicious vote count {count} (too large)")
            return False
        
        # Check for suspicious jumps (more than 100 votes difference)
        if previous is not None:
            diff = abs(count - previous)
            if diff > 100:
                logger.warning(f"{name}: Suspicious vote jump: {previous} -> {count} (diff: {diff})")
                # Still accept it, but log it
        
        return True

    def _extract_with_beautifulsoup(self, html: str, site_name: str) -> Optional[int]:
        """
        Extract vote count using BeautifulSoup CSS selectors.
        This is the most reliable method as it targets specific HTML elements.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Minecraft-MP: Look for "Vote(s)" in table
            if site_name == "Minecraft-MP":
                # Find the table row with "Vote(s)"
                for row in soup.find_all('tr'):
                    if row.find('strong') and 'Vote(s)' in row.find('strong').get_text():
                        # The next td should contain the number
                        tds = row.find_all('td')
                        if len(tds) >= 2:
                            vote_text = tds[1].get_text().strip()
                            # Extract number from text
                            match = re.search(r'\d+', vote_text)
                            if match:
                                return int(match.group())
            
            # MinecraftServers.org: Look for "Votes" row
            elif site_name == "MinecraftServers.org":
                # Find div with "Votes" text
                for row in soup.find_all('div', class_='row'):
                    cols = row.find_all('div')
                    if len(cols) >= 2:
                        label = cols[0].get_text().strip()
                        if label == "Votes":
                            vote_text = cols[1].get_text().strip()
                            match = re.search(r'\d+', vote_text)
                            if match:
                                return int(match.group())
            
            # Minecraft-Server-List: Look for "Players have voted"
            elif site_name == "Minecraft-Server-List":
                # Look for text containing "Players have voted"
                text = soup.get_text()
                match = re.search(r'(\d+)\s+Players have voted', text)
                if match:
                    return int(match.group(1))
                
                # Alternative: Look for "Votes - All time"
                match = re.search(r'<b>(\d+)\s+Votes\s*-\s*All time</b>', html)
                if match:
                    return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"{site_name}: BeautifulSoup extraction error - {e}")
            return None

    def _extract_with_regex(self, html: str, site: dict) -> Optional[int]:
        """
        Extract vote count using regex patterns (fallback method).
        """
        for pattern in site.get("fallback_patterns", []):
            try:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    return int(match.group(1))
            except Exception as e:
                logger.debug(f"{site['name']}: Regex pattern failed - {e}")
                continue
        return None

    async def scrape_site(self, site: dict, max_retries: int = 2) -> tuple[str, Optional[int]]:
        """
        Scrape a single site for its vote count with retry logic.
        Tries multiple extraction strategies for maximum reliability.
        """
        name = site["name"]
        url = site["url"]
        
        # Track attempts
        if name not in self.scrape_attempts:
            self.scrape_attempts[name] = {"success": 0, "fail": 0}

        for attempt in range(max_retries + 1):
            try:
                # Get HTML content
                if name == "Minecraft-Server-List":
                    html = await self._fetch_with_cloudscraper(url, name)
                else:
                    html = await self._fetch_with_aiohttp(url, name)
                
                if not html:
                    if attempt < max_retries:
                        logger.info(f"{name}: Retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(1)  # Wait before retry
                        continue
                    return self._get_cached_or_none(name)

                # Strategy 1: BeautifulSoup (most reliable)
                count = self._extract_with_beautifulsoup(html, name)
                if count is not None and self._validate_vote_count(name, count, self.last_successful_counts.get(name)):
                    logger.info(f"{name}: Found {count} votes (BeautifulSoup)")
                    self.last_successful_counts[name] = count
                    self.scrape_attempts[name]["success"] += 1
                    return name, count

                # Strategy 2: Regex patterns (fallback)
                count = self._extract_with_regex(html, site)
                if count is not None and self._validate_vote_count(name, count, self.last_successful_counts.get(name)):
                    logger.info(f"{name}: Found {count} votes (Regex)")
                    self.last_successful_counts[name] = count
                    self.scrape_attempts[name]["success"] += 1
                    return name, count

                # Both strategies failed
                logger.warning(f"{name}: Could not extract vote count (attempt {attempt + 1}/{max_retries + 1})")
                
                if attempt < max_retries:
                    await asyncio.sleep(1)  # Wait before retry
                    continue
                
                # All attempts failed
                self.scrape_attempts[name]["fail"] += 1
                return self._get_cached_or_none(name)

            except Exception as e:
                logger.error(f"{name}: Scrape error (attempt {attempt + 1}/{max_retries + 1}) - {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
                    continue
                self.scrape_attempts[name]["fail"] += 1
                return self._get_cached_or_none(name)

    async def _fetch_with_cloudscraper(self, url: str, name: str) -> Optional[str]:
        """Fetch HTML using cloudscraper for Cloudflare-protected sites."""
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=20)

            if response.status_code != 200:
                logger.warning(f"{name}: HTTP {response.status_code}")
                return None

            html = response.text
            logger.debug(f"{name}: Got {len(html)} bytes (via cloudscraper)")
            return html

        except Exception as e:
            logger.error(f"{name}: Cloudscraper error - {e}")
            return None

    async def _fetch_with_aiohttp(self, url: str, name: str) -> Optional[str]:
        """Fetch HTML using aiohttp."""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    return None

                html = await resp.text()
                logger.debug(f"{name}: Got {len(html)} bytes")
                return html

        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            return None
        except Exception as e:
            logger.error(f"{name}: Fetch error - {e}")
            return None

    def _get_cached_or_none(self, name: str) -> tuple[str, Optional[int]]:
        """Return cached value if available, otherwise None."""
        if name in self.last_successful_counts:
            logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
            return name, self.last_successful_counts[name]
        logger.warning(f"{name}: No cached value available")
        return name, None

    async def scrape_all(self) -> tuple[dict[str, Optional[int]], int]:
        """
        Scrape all configured sites sequentially with small delays.
        Returns (site_counts_dict, total_sum).
        """
        if not self.session:
            await self.start()

        counts = {}
        total = 0

        for i, site in enumerate(VOTE_SITES):
            name, count = await self.scrape_site(site)
            counts[name] = count
            if count is not None:
                total += count

            # Small delay between sites to avoid rate limiting
            if i < len(VOTE_SITES) - 1:
                await asyncio.sleep(1)

        logger.info(f"Scrape complete: {counts} | Total: {total}")
        
        # Log success rates
        for name, stats in self.scrape_attempts.items():
            total_attempts = stats["success"] + stats["fail"]
            if total_attempts > 0:
                success_rate = (stats["success"] / total_attempts) * 100
                logger.debug(f"{name}: Success rate {success_rate:.1f}% ({stats['success']}/{total_attempts})")

        return counts, total

    def get_stats(self) -> dict:
        """Get scraper statistics for debugging."""
        return {
            "last_successful_counts": self.last_successful_counts.copy(),
            "scrape_attempts": self.scrape_attempts.copy(),
        }
