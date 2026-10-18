"""
Web scraper for vote count sites.
"""

import re
import asyncio
import logging
from typing import Optional
import aiohttp
import cloudscraper
from config import VOTE_SITES

logger = logging.getLogger("VotePartyBot")


class VoteScraper:
    """
    Scrapes vote counts from Minecraft server list websites.
    Uses regex fallbacks and cloudscraper for Cloudflare-protected sites.
    Includes caching to prevent data loss when scrapes fail.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_successful_counts: dict[str, int] = {}

    async def start(self):
        """Initialize the HTTP session with proper headers."""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

    def _validate_vote_count(self, name: str, count: int) -> bool:
        """Validate that a vote count is reasonable."""
        if count < 0:
            logger.warning(f"{name}: Invalid vote count {count} (negative)")
            return False
        if count > 1000000:
            logger.warning(f"{name}: Suspicious vote count {count} (too large)")
            return False
        return True

    async def scrape_site(self, site: dict) -> tuple[str, Optional[int]]:
        """
        Scrape a single site for its vote count.
        Uses regex on raw HTML for maximum reliability.
        Uses cloudscraper for Cloudflare-protected sites.
        """
        name = site["name"]
        url = site["url"]

        # Minecraft-Server-List uses Cloudflare
        if name == "Minecraft-Server-List":
            return await self._scrape_with_cloudscraper(site)

        # For other sites, use regular aiohttp
        return await self._scrape_with_aiohttp(site)

    async def _scrape_with_cloudscraper(self, site: dict) -> tuple[str, Optional[int]]:
        """Scrape using cloudscraper for Cloudflare-protected sites."""
        name = site["name"]
        url = site["url"]

        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=20)

            if response.status_code != 200:
                logger.warning(f"{name}: HTTP {response.status_code}")
                return self._get_cached_or_none(name)

            html = response.text
            logger.info(f"{name}: Got {len(html)} bytes (via cloudscraper)")

            for pattern in site["fallback_patterns"]:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    count = int(match.group(1))
                    if self._validate_vote_count(name, count):
                        logger.info(f"{name}: Found {count} votes")
                        self.last_successful_counts[name] = count
                        return name, count

            logger.warning(f"{name}: Could not find vote count")
            return self._get_cached_or_none(name)

        except Exception as e:
            logger.error(f"{name}: Cloudscraper error - {e}")
            return self._get_cached_or_none(name)

    async def _scrape_with_aiohttp(self, site: dict) -> tuple[str, Optional[int]]:
        """Scrape using regular aiohttp."""
        name = site["name"]
        url = site["url"]

        try:
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    return self._get_cached_or_none(name)

                html = await resp.text()
                logger.info(f"{name}: Got {len(html)} bytes")

                for pattern in site["fallback_patterns"]:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        count = int(match.group(1))
                        if self._validate_vote_count(name, count):
                            logger.info(f"{name}: Found {count} votes")
                            self.last_successful_counts[name] = count
                            return name, count

                logger.warning(f"{name}: Could not find vote count")
                return self._get_cached_or_none(name)

        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            return self._get_cached_or_none(name)
        except Exception as e:
            logger.error(f"{name}: Scrape error - {e}")
            return self._get_cached_or_none(name)

    def _get_cached_or_none(self, name: str) -> tuple[str, Optional[int]]:
        """Return cached value if available, otherwise None."""
        if name in self.last_successful_counts:
            logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
            return name, self.last_successful_counts[name]
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

            # Small delay between sites
            if i < len(VOTE_SITES) - 1:
                await asyncio.sleep(1)

        logger.info(f"Scrape complete: {counts} | Total: {total}")
        return counts, total
