#!/usr/bin/env python3
"""
Complete site crawler: Extract ALL links first, then filter by keywords.
Works with any domain to find policy/help pages.
"""

import asyncio
import json
import logging
import re
import sys
import time
import requests
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import gzip

import httpx
from lxml import etree, html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Keywords for filtering and scoring
KEYWORDS_PRIMARY = [
    "shipping", "delivery", "returns", "return", "refund", "exchange", "exchanges",
    "warranty", "guarantee"
]

KEYWORDS_SECONDARY = [
    "policy", "policies", "help", "support", "faq", "faqs", "customer-service",
    "customer-care", "care", "assistance", "contact", "about"
]

# Insurance and protection related keywords
INSURANCE_KEYWORDS = [
    "insurance", "protection", "coverage", "assurance", "secure", "safety",
    "extended-warranty", "extended-warranties", "protection-plan", "protection-plans",
    "accident-protection", "damage-protection", "loss-protection", "theft-protection",
    "water-protection", "drop-protection", "screen-protection", "device-protection",
    "product-protection", "purchase-protection", "shipping-insurance", "delivery-insurance",
    "return-insurance", "refund-protection", "money-back-guarantee", "satisfaction-guarantee",
    "lifetime-warranty", "limited-warranty", "full-warranty", "partial-warranty",
    "repair-warranty", "replacement-warranty", "upgrade-protection", "trade-in-protection"
]

# Cart and shopping related keywords
CART_KEYWORDS = [
    "cart", "shopping-cart", "basket", "checkout", "payment", "order",
    "purchase", "buy", "add-to-cart", "shopping", "store", "shop",
    "product", "collection", "wishlist", "favorites", "account", "login"
]

PATH_KEYWORDS = [
    "return-policy", "returns-policy", "shipping-policy", "delivery-policy",
    "how-to-return", "howtoreturn", "returns-exchanges", "shipping-delivery",
    "help-center", "customer-care", "customer-service", "support-center"
]

# Noise patterns to avoid (excluding cart-related as they're now wanted)
NOISE_PATTERNS = [
    "/products/", "/product/", "/collections/", "/search",
    "/signin", "/signup", "/register", "/blog/", "/news/", "/press/", "?", "#"
]

# Non-English locales to skip
NON_EN_LOCALES = [
    "/fr/", "/es/", "/de/", "/it/", "/jp/", "/zh/", "/pt/", "/ru/",
    "/mx/", "/cl/", "/cr/", "/ar/", "/br/", "/co/", "/pe/", "/uy/",
    "/ve/", "/uk/", "/tr/", "/kz/", "/kh/", "/nl/", "/sv/", "/da/"
]


class CompleteCrawler:
    def __init__(self, domain: str, max_pages: int = 1000):
        self.domain = domain
        self.max_pages = max_pages
        self.base_url = f"https://{domain}"
        self.found_urls: Set[str] = set()
        self.crawled_urls: Set[str] = set()
        self.policy_urls: List[Tuple[int, str]] = []
        
    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to same domain."""
        try:
            parsed = urlparse(url)
            return self.domain.lower() in parsed.netloc.lower()
        except:
            return False
    
    def is_english_url(self, url: str) -> bool:
        """Check if URL is likely English (avoid non-EN locales)."""
        url_lower = url.lower()
        return not any(locale in url_lower for locale in NON_EN_LOCALES)
    
    def is_us_url(self, url: str) -> bool:
        """Check if URL is US-specific or generic (no country code)."""
        url_lower = url.lower()
        
        # Allowed US patterns
        us_patterns = [
            "/us/", "/en-us/", "/us-en/", "/en_us/", "/us_en/",
        ]
        
        # Forbidden non-US patterns  
        non_us_patterns = [
            "/en-gb/", "/en-au/", "/en-ca/", "/en-nz/", "/en-eu/", 
            "/en-it/", "/en-ch/", "/gb/", "/au/", "/ca/", "/nz/",
            "/fr/", "/fr-", "/de/", "/es/", "/it/", "/pt/", "/ru/",
            "/zh/", "/jp/", "/kr/", "/mx/", "/br/", "/ar/", "/in/"
        ]
        
        # If has US pattern, it's US
        if any(pattern in url_lower for pattern in us_patterns):
            return True
            
        # If has non-US pattern, it's not US
        if any(pattern in url_lower for pattern in non_us_patterns):
            return False
            
        # If no country indicators, assume US (generic)
        return True
    
    def _test_url_content(self, url: str) -> bool:
        """Test if URL has valid content (not blocked/empty)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
            
            # Check for blocked pages
            if 'blocked?' in response.url.lower():
                logger.debug(f"🚫 Crawler: Blocked page detected: {url}")
                return False
                
            if response.status_code >= 400:
                logger.debug(f"🚫 Crawler: HTTP error {response.status_code}: {url}")
                return False
            
            # Quick content length check
            if len(response.text) < 500:
                logger.debug(f"🚫 Crawler: Content too short ({len(response.text)} chars): {url}")
                return False
                
            logger.info(f"✅ Crawler: Valid content: {url}")
            return True
            
        except Exception as e:
            logger.debug(f"🚫 Crawler: Content test failed for {url}: {e}")
            return False
    
    def score_url(self, url: str) -> int:
        """Score URL relevance for policy/help pages."""
        url_lower = url.lower()
        score = 0
        
        # Primary keywords (high value)
        for kw in KEYWORDS_PRIMARY:
            if kw in url_lower:
                score += 5
        
        # Secondary keywords
        for kw in KEYWORDS_SECONDARY:
            if kw in url_lower:
                score += 3
        
        # Path-specific keywords
        for kw in PATH_KEYWORDS:
            if kw in url_lower:
                score += 4
        
        # Cart and shopping keywords
        for kw in CART_KEYWORDS:
            if kw in url_lower:
                score += 2
        
        # Insurance and protection keywords (high priority)
        for kw in INSURANCE_KEYWORDS:
            if kw in url_lower:
                score += 6  # Higher score than primary keywords
        
        # Bonus for common policy paths
        if any(path in url_lower for path in ["/pages/", "/help/", "/support/", "/policies/"]):
            score += 2
        
        # Extra bonus for US-specific URLs
        if "/us/" in url_lower or "/en-us/" in url_lower:
            score += 3
        
        # Penalty for noise
        for noise in NOISE_PATTERNS:
            if noise in url_lower:
                score -= 2
        
        return max(0, score)
    
    async def fetch_url(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Fetch URL content with better error handling."""
        try:
            response = await client.get(url, follow_redirects=True)
            
            # Handle different HTTP status codes
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                logger.debug(f"Page not found (404): {url}")
                return None
            elif response.status_code == 403:
                logger.debug(f"Access forbidden (403): {url}")
                return None
            elif response.status_code >= 500:
                logger.warning(f"Server error {response.status_code} for {url}")
                return None
            else:
                logger.debug(f"HTTP {response.status_code} for {url}")
                return None
                
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
        return None
    
    async def fetch_sitemap_urls(self, client: httpx.AsyncClient) -> Set[str]:
        """Extract URLs from sitemaps."""
        urls = set()
        
        # Try robots.txt first
        robots_url = f"{self.base_url}/robots.txt"
        robots_content = await self.fetch_url(client, robots_url)
        sitemap_urls = []
        
        if robots_content:
            for line in robots_content.splitlines():
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_urls.append(sitemap_url)
        
        # Fallback sitemap locations
        if not sitemap_urls:
            sitemap_urls = [
                f"{self.base_url}/sitemap.xml",
                f"{self.base_url}/sitemap_index.xml",
                f"{self.base_url}/sitemap.xml.gz"
            ]
        
        # Process each sitemap
        for sitemap_url in sitemap_urls:
            await self.process_sitemap(client, sitemap_url, urls)
        
        logger.info(f"Found {len(urls)} URLs from sitemaps")
        return urls
    
    async def process_sitemap(self, client: httpx.AsyncClient, sitemap_url: str, urls: Set[str]):
        """Process a single sitemap file."""
        try:
            response = await client.get(sitemap_url, follow_redirects=True)
            if response.status_code != 200:
                return
            
            content = response.content
            
            # Handle gzipped content
            if sitemap_url.endswith('.gz'):
                try:
                    content = gzip.decompress(content)
                except:
                    pass
            
            # Parse XML
            root = etree.fromstring(content)
            
            # Extract URLs from sitemap
            for loc in root.xpath("//*[local-name()='loc']/text()"):
                url = loc.strip()
                if url and self.is_same_domain(url) and self.is_english_url(url) and self.is_us_url(url):
                    urls.add(url)
            
            # Check for sitemap index (nested sitemaps)
            for sitemap_loc in root.xpath("//*[local-name()='sitemap']/*[local-name()='loc']/text()"):
                nested_url = sitemap_loc.strip()
                if nested_url and nested_url != sitemap_url:
                    await self.process_sitemap(client, nested_url, urls)
        
        except Exception as e:
            logger.debug(f"Failed to process sitemap {sitemap_url}: {e}")
    
    def extract_links_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """Extract all links from HTML content (Google-style aggressive extraction)."""
        links = set()
        try:
            doc = html.fromstring(html_content)
            
            # Find all links (more aggressive)
            for element in doc.xpath('.//a[@href]'):
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    # Clean fragment and query params for crawling
                    parsed = urlparse(full_url)
                    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                    
                    # More permissive filtering - let's discover more URLs first
                    if (self.is_same_domain(clean_url) and 
                        clean_url not in self.crawled_urls):
                        links.add(clean_url)
            
            # Also look for form actions and other potential URLs
            for form in doc.xpath('.//form[@action]'):
                action = form.get('action')
                if action:
                    full_url = urljoin(base_url, action)
                    parsed = urlparse(full_url)
                    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                    if self.is_same_domain(clean_url) and clean_url not in self.crawled_urls:
                        links.add(clean_url)
            
            # Look for data attributes that might contain URLs
            for element in doc.xpath('.//*[@data-url]'):
                data_url = element.get('data-url')
                if data_url:
                    full_url = urljoin(base_url, data_url)
                    parsed = urlparse(full_url)
                    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                    if self.is_same_domain(clean_url) and clean_url not in self.crawled_urls:
                        links.add(clean_url)
        
        except Exception as e:
            logger.debug(f"Failed to extract links from HTML: {e}")
        
        return links
    
    async def crawl_page(self, client: httpx.AsyncClient, url: str) -> Set[str]:
        """Crawl a single page and extract links."""
        if url in self.crawled_urls or len(self.crawled_urls) >= self.max_pages:
            return set()
        
        self.crawled_urls.add(url)
        logger.debug(f"Crawling: {url}")
        
        html_content = await self.fetch_url(client, url)
        if not html_content:
            return set()
        
        # Extract new links from this page
        new_links = self.extract_links_from_html(html_content, url)
        
        return new_links
    
    async def run_complete_crawl(self) -> List[str]:
        """Run complete crawl: sitemaps + aggressive page crawling like Google."""
        timeout = httpx.Timeout(15.0)
        headers = {'User-Agent': USER_AGENT}
        
        async with httpx.AsyncClient(
            headers=headers, 
            timeout=timeout, 
            follow_redirects=True
        ) as client:
            
            # Step 1: Get URLs from sitemaps (if available)
            logger.info("Extracting URLs from sitemaps (if available)...")
            sitemap_urls = await self.fetch_sitemap_urls(client)
            self.found_urls.update(sitemap_urls)
            logger.info(f"Found {len(sitemap_urls)} URLs from sitemaps")
            
            # Step 2: Aggressive crawling starting from homepage and key pages
            logger.info("Starting aggressive page crawling (Google-style)...")
            
            # Start with homepage and common policy/help paths
            starting_urls = {
                self.base_url,
                f"{self.base_url}/help",
                f"{self.base_url}/support", 
                f"{self.base_url}/customer-service",
                f"{self.base_url}/contact",
                f"{self.base_url}/about",
                f"{self.base_url}/shipping",
                f"{self.base_url}/returns",
                f"{self.base_url}/policy",
                f"{self.base_url}/policies",
                f"{self.base_url}/faq",
                f"{self.base_url}/cart",
                f"{self.base_url}/checkout",
                f"{self.base_url}/account"
            }
            
            # Add insurance/protection path variations
            insurance_paths = [
                f"{self.base_url}/warranty",
                f"{self.base_url}/warranties", 
                f"{self.base_url}/insurance",
                f"{self.base_url}/protection",
                f"{self.base_url}/coverage",
                f"{self.base_url}/assurance",
                f"{self.base_url}/extended-warranty",
                f"{self.base_url}/protection-plan",
                f"{self.base_url}/damage-protection",
                f"{self.base_url}/accident-protection",
                f"{self.base_url}/pages/warranty",
                f"{self.base_url}/pages/insurance",
                f"{self.base_url}/pages/protection",
                f"{self.base_url}/pages/coverage",
                f"{self.base_url}/pages/extended-warranty"
            ]
            
            starting_urls.update(insurance_paths)
            
            to_crawl = starting_urls
            self.found_urls.update(starting_urls)
            
            # Also try common US-specific paths
            us_paths = [
                f"{self.base_url}/us",
                f"{self.base_url}/us/en",
                f"{self.base_url}/en-us",
                f"{self.base_url}/us/help",
                f"{self.base_url}/us/support",
                f"{self.base_url}/us/shipping",
                f"{self.base_url}/us/returns"
            ]
            
            for us_path in us_paths:
                if us_path not in self.found_urls:
                    to_crawl.add(us_path)
                    self.found_urls.add(us_path)
            
            while to_crawl and len(self.crawled_urls) < self.max_pages:
                # Take batch of URLs to crawl
                current_batch = list(to_crawl)[:15]  # Process 15 at a time for more aggressive crawling
                to_crawl = to_crawl - set(current_batch)
                
                # Crawl batch concurrently
                tasks = [self.crawl_page(client, url) for url in current_batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect new links
                for result in results:
                    if isinstance(result, set):
                        new_links = result - self.found_urls
                        self.found_urls.update(new_links)
                        to_crawl.update(new_links)
                
                logger.info(f"Crawled: {len(self.crawled_urls)}, Found: {len(self.found_urls)}, Queue: {len(to_crawl)}")
                
                # Shorter delay for more aggressive crawling
                await asyncio.sleep(1.5)
        
        # Step 3: Filter URLs for valid content BEFORE scoring
        logger.info("🔍 Pre-filtering crawled URLs for valid content...")
        valid_found_urls = []
        
        # Limit URLs to test (avoid infinite crawling)
        urls_to_test = list(self.found_urls)[:100]  # Only test first 100 URLs
        logger.info(f"🔍 Testing {len(urls_to_test)} URLs out of {len(self.found_urls)} found")
        
        for url in urls_to_test:
            if self._test_url_content(url):
                valid_found_urls.append(url)
        
        logger.info(f"✅ Crawler content validation: {len(valid_found_urls)}/{len(self.found_urls)} URLs have valid content")
        
        # Step 4: Score and filter URLs with category limits  
        logger.info("Scoring and filtering URLs with category limits...")
        for url in valid_found_urls:
            score = self.score_url(url)
            if score > 0:  # Only keep URLs with positive scores
                self.policy_urls.append((score, url))
        
        # Sort by score (highest first)
        self.policy_urls.sort(key=lambda x: (-x[0], x[1]))
        
        # Apply category limits (max 2 per category)
        final_urls = self._apply_category_limits([url for score, url in self.policy_urls])
        
        return final_urls
    
    def _apply_category_limits(self, urls: List[str]) -> List[str]:
        """Apply category limits to ensure max 2 URLs per category."""
        # Define categories for limiting results
        CATEGORIES = {
            "policy_help": ["shipping", "returns", "refund", "exchange", "help", "support", "faq", "policy", "warranty"],
            "insurance_protection": ["insurance", "protection", "coverage", "assurance", "extended-warranty", "protection-plan", "damage-protection", "accident-protection"],
            "cart_shopping": ["cart", "checkout", "payment", "order", "shopping", "account", "login", "basket", "purchase"],
            "contact_about": ["contact", "about", "customer-care", "assistance"]
        }
        
        category_counts = {cat: 0 for cat in CATEGORIES.keys()}
        final_urls = []
        
        for url in urls:
            url_lower = url.lower()
            
            # Determine category
            category = None
            for cat_name, keywords in CATEGORIES.items():
                if any(kw in url_lower for kw in keywords):
                    category = cat_name
                    break
            
            if category and category_counts[category] < 2:
                final_urls.append(url)
                category_counts[category] += 1
                logger.debug(f"Added {url} to category {category} (count: {category_counts[category]})")
            elif category is None:  # Uncategorized URLs
                final_urls.append(url)
                logger.debug(f"Added {url} (uncategorized)")
        
        logger.info(f"Category limits applied: {category_counts}")
        return final_urls


def _filter_valid_content_urls(urls: List[str], domain: str) -> List[str]:
    """Filter URLs by keywords first, then validate with fast HTTP requests"""
    valid_urls = []
    
    # Categorize URLs by keywords and limit per category
    categories = {
        'shipping': ['shipping', 'delivery', 'fulfillment'],
        'returns': ['return', 'refund', 'exchange'],
        'help': ['help', 'support', 'faq', 'customer'],
        'insurance': ['insurance', 'protection', 'warranty', 'coverage'],
        'policy': ['policy', 'terms', 'conditions']
    }
    
    # Track URLs per category (max 3 per category)
    category_counts = {cat: 0 for cat in categories.keys()}
    candidate_urls = []
    
    # Step 1: Pre-filter by keywords (fast)
    logger.info(f"🔍 Step 1: Pre-filtering {len(urls)} URLs by keywords...")
    
    for url in urls:
        url_lower = url.lower()
        
        # Skip obvious non-policy URLs quickly
        skip_patterns = [
            '/product/', '/item/', '/search', '/category/', '/catalog/',
            '/browse/', '/shop/', '/deals/', '/sale', '/brand/',
            '.jpg', '.png', '.pdf', '.css', '.js'
        ]
        
        if any(pattern in url_lower for pattern in skip_patterns):
            continue
        
        # Check categories
        for category, keywords in categories.items():
            if category_counts[category] < 3:  # Max 3 per category
                if any(keyword in url_lower for keyword in keywords):
                    candidate_urls.append(url)
                    category_counts[category] += 1
                    logger.debug(f"📝 Candidate {category} URL: {url}")
                    break
    
    logger.info(f"📝 Found {len(candidate_urls)} candidate URLs: {category_counts}")
    
    # Step 2: Validate candidates with fast HTTP requests
    logger.info(f"🔍 Step 2: Validating {len(candidate_urls)} candidates with HTTP requests...")
    
    for i, url in enumerate(candidate_urls, 1):
        try:
            logger.info(f"⚡ Testing {i}/{len(candidate_urls)}: {url[:60]}...")
            
            # SUPER FAST HTTP check
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=3, allow_redirects=True)
            
            # Quick checks
            if 'blocked?' in response.url.lower():
                logger.debug(f"❌ Blocked: {url}")
                continue
                
            if response.status_code >= 400:
                logger.debug(f"❌ HTTP {response.status_code}: {url}")
                continue
            
            if len(response.text) < 300:
                logger.debug(f"❌ Too short ({len(response.text)} chars): {url}")
                continue
            
            # Quick content check
            text_lower = response.text.lower()
            if any(indicator in text_lower for indicator in ['page not found', 'access denied', 'forbidden']):
                logger.debug(f"❌ Error page: {url}")
                continue
            
            # Success!
            valid_urls.append(url)
            logger.info(f"✅ Valid: {url}")
            
        except Exception as e:
            logger.debug(f"❌ Failed {url}: {e}")
            continue
    
    logger.info(f"✅ Final result: {len(valid_urls)} valid URLs from {len(urls)} original URLs")
    
    return valid_urls


def google_search_urls(domain: str, api_key: str, cx: str, max_results: int = 100) -> List[str]:
    """Search Google for URLs on a domain using Custom Search API."""
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    # Build search queries for policy/help pages (more targeted)
    queries = [
        f'site:{domain} (shipping OR returns OR refund OR exchanges OR policy)',
        f'site:{domain} (help OR support OR faq OR customer-service)',
        f'site:{domain} (insurance OR protection OR coverage OR warranty OR assurance)',
        f'site:{domain} (extended-warranty OR protection-plan OR damage-protection)',
        f'site:{domain} (cart OR checkout OR account OR login)',
        f'site:{domain} (contact OR about OR assistance)',
        # More specific insurance queries
        f'site:{domain} (warranty-policy OR insurance-policy OR protection-policy)',
        f'site:{domain} (product-protection OR device-protection OR screen-protection)',
        f'site:{domain} (accident-protection OR water-protection OR drop-protection)'
    ]
    
    all_urls = []
    
    for query in queries:
        try:
            params = {
                'key': api_key,
                'cx': cx,
                'q': query,
                'num': 10,
                'hl': 'en',
                'gl': 'us'
            }
            
            response = requests.get(base_url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            if 'items' in data:
                for item in data['items']:
                    url = item.get('link', '')
                    if url and url not in all_urls:
                        all_urls.append(url)
            
            # Small delay between requests
            time.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Google search failed for query '{query}': {e}")
    
    logger.info(f"Google Search found {len(all_urls)} URLs")
    
    # Filter out empty/blocked pages
    if all_urls:
        logger.info("🔍 Filtering out empty/blocked pages...")
        valid_urls = _filter_valid_content_urls(all_urls, domain)
        logger.info(f"✅ Content validation: {len(valid_urls)}/{len(all_urls)} URLs have valid content")
        return valid_urls
    
    return all_urls


async def find_policy_links(domain: str, limit: int = 20, max_pages: int = 500, use_google: bool = True) -> List[str]:
    """Find policy/help links for a domain using Google Search + crawling."""
    
    # Step 1: Google Search (always used)
    logger.info("🔍 Step 1: Searching Google for URLs...")
    
    # Use your API credentials
    api_key = "AIzaSyBRV7cTzszZ8fnWwuAENO6p4JV2zgy_fR4"
    cx = "7135af6aa74714f65"
    
    google_urls = google_search_urls(domain, api_key, cx)
    
    # Step 2: Crawling (as backup and to find more URLs)
    logger.info("🕷️  Step 2: Crawling for additional URLs...")
    crawler = CompleteCrawler(domain, max_pages)
    
    # Filter Google URLs before adding to crawler
    if google_urls:
        logger.info("🔍 Pre-filtering Google URLs for valid content...")
        valid_google_urls = _filter_valid_content_urls(google_urls, domain)
        logger.info(f"✅ Google URL validation: {len(valid_google_urls)}/{len(google_urls)} URLs have valid content")
        crawler.found_urls.update(valid_google_urls)
    
    all_policy_links = await crawler.run_complete_crawl()
    
    logger.info(f"Total found: {len(all_policy_links)} policy-related URLs")
    
    return all_policy_links[:limit]


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Find policy/help pages for any domain')
    parser.add_argument('--domain', help='Target domain')
    parser.add_argument('--limit', type=int, default=30, help='Max URLs to return')
    parser.add_argument('--max-pages', type=int, default=300, help='Max pages to crawl')
    parser.add_argument('--quiet', action='store_true', help='Only show URLs, no logs')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Get domain from user
    if args.domain:
        domain = args.domain
    else:
        try:
            domain = input('Enter domain (e.g., example.com): ').strip()
        except KeyboardInterrupt:
            return
    
    if not domain:
        print('Domain is required.', file=sys.stderr)
        return
    
    if not args.quiet:
        print(f"\n🔍 Crawling {domain} for policy/help pages...\n")
    
    start_time = time.time()
    
    try:
        policy_links = await find_policy_links(domain, limit=args.limit, max_pages=args.max_pages)
        
        if args.quiet:
            for url in policy_links:
                print(url)
        else:
            print(f"\n✅ Found {len(policy_links)} policy/help URLs (sorted by relevance):\n")
            
            for i, url in enumerate(policy_links, 1):
                print(f"{i:2d}. {url}")
        
            elapsed = time.time() - start_time
            print(f"\n⏱️  Completed in {elapsed:.1f}s")
        
    except Exception as e:
        logger.error(f"Crawling failed: {e}")


if __name__ == '__main__':
    asyncio.run(main())
