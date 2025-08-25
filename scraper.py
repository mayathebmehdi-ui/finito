
import asyncio
import re
from urllib.parse import urlparse
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
# Optional legacy helper removed by cleanup; provide a no-op fallback
def find_policy_links(domain: str, limit: int = 10, max_pages: int = 50):
    return []

class EcommerceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def scrape_website(self, url: str) -> Dict:
        """NEW OPTIMIZED scraper - uses complete_crawler to find ALL links first"""
        domain = urlparse(url).netloc
        
        scraped_content = {
            'domain': domain,
            'main_url': url,
            'policy_pages': {}
        }
        
        try:
            print(f"🔍 Scraping {url}...")
            
            # STEP 1: Get main page with requests (fast)
            main_content = self._get_page_content_requests(url)
            if main_content:
                scraped_content['policy_pages']['main'] = {
                    'url': url,
                    'content': main_content
                }
                print(f"✅ Main page scraped: {len(main_content)} chars")
            
            # STEP 2: Decide path based on Shopify detection
            try:
                if await self._is_shopify_site(domain):
                    print("  🛍️ Shopify site detected, using smart approach...")
                    scraped_content['is_shopify'] = True
                    policy_urls = await self._get_shopify_policy_urls(domain)
                    print(f"🔗 Found {len(policy_urls)} Shopify policy URLs")
                else:
                    print("  🔥 Non-Shopify site: skipping internal crawl; Firecrawl will handle discovery")
                    scraped_content['is_shopify'] = False
                    return scraped_content
            except Exception as e:
                print(f"  ⚠️ Shopify detection error: {e}")
                scraped_content['is_shopify'] = False
                return scraped_content
            
            # STEP 3: SCRAPE ALL PAGES - let AI decide what's useful
            scraped_count = 0
            max_pages = 10  # Scrape more pages for better AI analysis
            
            print(f"  📚 Scraping ALL policy pages for comprehensive AI analysis...")
            
            for i, page_url in enumerate(policy_urls, 1):
                # ONLY stop if we hit the limit
                if scraped_count >= max_pages:
                    print(f"  ⏹️ Reached limit of {max_pages} pages")
                    break
                    
                try:
                    print(f"  📄 [{i}/{len(policy_urls)}] Scraping: {page_url}")
                    
                    # USE PLAYWRIGHT FOR ALL SITES - no more BeautifulSoup corruption
                    print(f"    🎭 Using Playwright for clean content extraction...")
                    content = await self._get_clean_content_playwright(page_url)
                    
                    if content and len(content) > 200:  # Minimum content threshold
                        page_type = self._classify_page_type(page_url, content)
                        
                        # STORE ALL PAGES - no skipping duplicates, let AI choose
                        page_key = f"{page_type}_{i}" if page_type in scraped_content['policy_pages'] else page_type
                        
                        scraped_content['policy_pages'][page_key] = {
                            'url': page_url,
                            'content': content
                        }
                        scraped_count += 1
                        
                        print(f"    📝 Stored as: {page_key} ({len(content)} chars)")
                        
                        # Add human-like delay between requests
                        import time
                        time.sleep(1.5)  # 1.5 second delay to avoid being flagged as bot
                    else:
                        print(f"    🚫 Page skipped (404/not found or too short content)")
                        
                except Exception as e:
                    print(f"  ❌ Error scraping {page_url}: {e}")
                    continue
            
            print(f"📄 Total pages scraped: {len(scraped_content['policy_pages'])}")
            print(f"📚 ALL pages will be sent to AI for comprehensive analysis")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        
        return scraped_content

    def _classify_page_type(self, url: str, content: str) -> str:
        """Classify page type based on URL and content"""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # Check URL patterns first
        if any(kw in url_lower for kw in ['shipping', 'delivery', 'fulfillment']):
            return 'shipping'
        elif any(kw in url_lower for kw in ['return', 'refund', 'exchange']):
            return 'returns'
        elif any(kw in url_lower for kw in ['faq', 'help', 'support']):
            return 'help'
        elif any(kw in url_lower for kw in ['contact', 'about']):
            return 'contact'
        
        # Check content patterns
        shipping_score = sum(1 for kw in ['shipping', 'delivery', 'fulfillment', 'ship'] if kw in content_lower)
        returns_score = sum(1 for kw in ['return', 'refund', 'exchange'] if kw in content_lower)
        
        if shipping_score > returns_score and shipping_score > 2:
            return 'shipping'
        elif returns_score > 2:
            return 'returns'
        else:
            return 'policy'
    
    def _extract_text_from_json(self, data) -> str:
        """Extract all text content from JSON data (general approach)"""
        text_content = ""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 10:
                    # Check if this text contains policy-related content
                    if any(keyword in value.lower() for keyword in ['shipping', 'return', 'policy', 'delivery', 'refund', 'exchange', 'final sale', 'free shipping']):
                        text_content += f"{key}: {value}\n"
                elif isinstance(value, (dict, list)):
                    text_content += self._extract_text_from_json(value)
        elif isinstance(data, list):
            for item in data:
                text_content += self._extract_text_from_json(item)
        
        return text_content
    
    async def _get_prioritized_policy_urls(self, domain: str) -> List[str]:
        """Get policy URLs prioritized by AI and help domain checks"""
        import openai
        import os
        
        all_urls = []
        
        # STEP 1: Check help/support subdomains first (most likely to have policies)
        help_domains = [
            f"https://help.{domain}",
            f"https://support.{domain}",
            f"https://faq.{domain}",
            f"https://care.{domain}"
        ]
        
        print("  🔍 Checking help/support domains...")
        for help_url in help_domains:
            if await self._domain_exists(help_url):
                print(f"    ✅ Found active help domain: {help_url}")
                # Get URLs from this help domain
                help_urls = await find_policy_links(help_url.replace('https://', ''), limit=10, max_pages=50)
                all_urls.extend(help_urls[:10])  # Take top 10 from help domain
                break  # Stop at first working help domain
        
        # STEP 2: If no help domain, crawl main domain with multiple fallbacks
        if not all_urls:
            print("  🔄 No help domain found, crawling main domain...")
            try:
                # Check if it's a Shopify site (common rate limiting)
                if await self._is_shopify_site(domain):
                    print("  🛍️ Shopify site detected, using smart approach...")
                    main_urls = await self._get_shopify_policy_urls(domain)
                else:
                    main_urls = await find_policy_links(domain, limit=20, max_pages=100)
                all_urls.extend(main_urls)
                
                # TRIGGER FALLBACKS if no URLs found (not just on exceptions)
                if len(all_urls) == 0:
                    print("  ⚠️ No URLs found, trying fallback methods...")
                    
                    # FALLBACK LEVEL 1: Try complete crawler with more aggressive approach
                    try:
                        print("  🔍 Using complete crawler fallback...")
                        advanced_urls = await self._advanced_crawler_fallback(domain)
                        all_urls.extend(advanced_urls)
                    except Exception as e2:
                        print(f"  ⚠️ Advanced crawler failed ({e2})")
                    
                    # FALLBACK LEVEL 2: Manual policy URLs (for sites like Zara)
                    if len(all_urls) == 0:
                        print("  🎯 Using manual policy URLs fallback...")
                        manual_urls = await self._get_manual_policy_urls(domain)
                        all_urls.extend(manual_urls)
                        
            except Exception as e:
                print(f"  ⚠️ Main crawling failed ({e}), trying fallbacks...")
                
                # FALLBACK LEVEL 1: Try complete crawler with more aggressive approach
                try:
                    print("  🔍 Using complete crawler fallback...")
                    advanced_urls = await self._advanced_crawler_fallback(domain)
                    all_urls.extend(advanced_urls)
                except Exception as e2:
                    print(f"  ⚠️ Advanced crawler failed ({e2})")
                
                # FALLBACK LEVEL 2: Manual policy URLs (for sites like Zara)
                if len(all_urls) == 0:
                    print("  🎯 Using manual policy URLs fallback...")
                    manual_urls = await self._get_manual_policy_urls(domain)
                    all_urls.extend(manual_urls)
        
        # STEP 3: Use OpenAI to prioritize URLs by relevance
        if len(all_urls) > 5 and os.getenv("OPENAI_API_KEY"):
            print("  🤖 Using AI to prioritize URLs...")
            prioritized_urls = await self._ai_prioritize_urls(all_urls)
            return prioritized_urls[:10]  # Top 10 most relevant
        
        return all_urls[:10]  # Fallback: take first 10
    
    async def _domain_exists(self, url: str) -> bool:
        """Check if domain/subdomain exists and responds"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    async def _ai_prioritize_urls(self, urls: List[str]) -> List[str]:
        """Use OpenAI to prioritize URLs by relevance for shipping/returns policies"""
        import openai
        import os
        
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            urls_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls)])
            
            prompt = f"""Prioritize these URLs by relevance for finding shipping and return policies. 
Return ONLY the numbers (1-{len(urls)}) in order of priority, comma-separated.
Focus on: shipping, delivery, returns, refunds, exchanges, FAQ, help, support, policy pages.

URLs:
{urls_text}

Priority order (numbers only):"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0
            )
            
            # Parse AI response
            priority_nums = response.choices[0].message.content.strip()
            priority_indices = [int(x.strip()) - 1 for x in priority_nums.split(',') if x.strip().isdigit()]
            
            # Reorder URLs based on AI priority
            prioritized = []
            for idx in priority_indices:
                if 0 <= idx < len(urls):
                    prioritized.append(urls[idx])
            
            # Add any missed URLs
            for url in urls:
                if url not in prioritized:
                    prioritized.append(url)
            
            print(f"    🎯 AI prioritized {len(prioritized)} URLs")
            return prioritized
            
        except Exception as e:
            print(f"    ⚠️ AI prioritization failed: {e}")
            return urls
    
    def _get_fallback_policy_urls(self, domain: str) -> List[str]:
        """Get common policy URLs as fallback when crawling fails"""
        base_url = f"https://{domain}"
        
        fallback_paths = [
            '/pages/shipping-policy', '/pages/shipping-information', '/pages/shipping',
            '/pages/return-policy', '/pages/returns-exchanges', '/pages/returns',
            '/pages/faq', '/pages/help', '/pages/support', '/pages/customer-service',
            '/help', '/support', '/faq', '/shipping', '/returns', '/policies',
            '/customer-service', '/customer-care', '/contact-us', '/about-us'
        ]
        
        return [f"{base_url}{path}" for path in fallback_paths]
    
    async def _is_shopify_site(self, domain: str) -> bool:
        """Detect if site is Shopify using multiple reliable signals"""
        base_url = f"https://{domain}"
        
        try:
            # 1) Headers check - most reliable
            response = self.session.head(base_url, timeout=12)
            headers = {k.lower(): v for k, v in response.headers.items()}
            
            if any(k.startswith("x-shopify") or k.startswith("x-sorting-hat") for k in headers):
                print(f"    🛍️ Shopify detected via headers")
                return True
            
            # 2) Cookies check
            set_cookie = response.headers.get("set-cookie", "").lower()
            if any(k in set_cookie for k in ["_shopify_", "cart_sig"]):
                print(f"    🛍️ Shopify detected via cookies")
                return True
            
        except Exception:
            pass

        # 3) Shopify endpoints check
        for path in ["/cart.js", "/products.json"]:
            try:
                response = self.session.get(base_url + path, timeout=12, headers={"Accept": "application/json"})
                if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
                    print(f"    🛍️ Shopify detected via endpoint {path}")
                    return True
                await asyncio.sleep(1.0)  # Delay between endpoint checks
            except Exception:
                pass

        # 4) HTML content check (last resort)
        try:
            response = self.session.get(base_url, timeout=12)
            text = response.text
            if any(signal in text for signal in ["window.Shopify", "ShopifyAnalytics", "cdn.shopify.com", "/s/files/1/"]):
                print(f"    🛍️ Shopify detected via HTML content")
                return True
        except Exception:
            pass

        return False
    
    async def _get_shopify_policy_urls(self, domain: str) -> List[str]:
        """Get policy URLs for Shopify sites using known patterns + Playwright for JS content"""
        base_url = f"https://{domain}"
        
        # Shopify canonical URLs (highest priority)
        shopify_paths = [
            '/policies/shipping-policy', '/policies/refund-policy', '/policies/return-policy',
            '/policies/terms-of-service', '/policies/privacy-policy',
            '/pages/shipping-policy', '/pages/shipping-information', '/pages/shipping',
            '/pages/return-policy', '/pages/returns-exchanges', '/pages/returns',
            '/pages/refund-policy', '/pages/exchange-policy',
            '/pages/faq', '/pages/help', '/pages/customer-service'
        ]
        
        # Quick test for existing URLs
        valid_urls = []
        for path in shopify_paths[:8]:  # Test top 8 only
            try:
                url = f"{base_url}{path}"
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    valid_urls.append(url)
                    print(f"    ✅ Found Shopify page: {path}")
                
                import time
                time.sleep(1.5)  # Faster for URL testing
                
            except Exception:
                continue
        
        return valid_urls
    
    async def _get_clean_content_playwright(self, url: str) -> Optional[str]:
        """Extract clean content using Playwright (for ALL sites - no BeautifulSoup corruption)"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                    }
                )
                page = await context.new_page()
                
                # Stealth: remove webdriver traces
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Mock plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Mock languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """)
                
                # For Walmart help pages: preload homepage to get session cookies
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                if 'walmart.com' in parsed_url.netloc and '/help/' in url:
                    print(f"    🍪 Preloading Walmart homepage for session cookies...")
                    try:
                        await page.goto(f"{parsed_url.scheme}://{parsed_url.netloc}", timeout=15000, wait_until='domcontentloaded')
                        await page.wait_for_timeout(2000)  # Let cookies set
                    except:
                        pass  # Continue even if homepage fails
                
                # Navigate to target page
                await page.goto(url, timeout=30000, wait_until='networkidle')
                
                # Wait for dynamic content and potential anti-bot checks
                await page.wait_for_timeout(3000)
                
                # Try to wait for main content to load
                try:
                    await page.wait_for_selector('main, [role="main"], .main-content, .content', timeout=5000)
                except:
                    pass  # Continue if no main content selector found
                await page.wait_for_timeout(3000)  # Wait for JS to load content
                
                # Extract PERFECT clean text content
                # Detect WAF blocks via URL
                final_url = page.url
                if 'walmart.com/blocked?' in final_url:
                    print(f"    🚫 WAF block detected at {final_url}")
                content = await page.evaluate('''() => {
                    // Remove all problematic elements
                    const elementsToRemove = document.querySelectorAll('script, style, nav, header, footer, aside, noscript');
                    elementsToRemove.forEach(el => el.remove());
                    
                    // Get main content with priority selectors
                    const selectors = [
                        'main', '[role="main"]', '.main-content', '.content',
                        '.policy-content', '.page-content', '.rte', '.shopify-policy__container',
                        'article', '.article', '[class*="policy"]', '[class*="shipping"]', '[class*="return"]'
                    ];
                    
                    let mainElement = null;
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.innerText.length > 200) {
                            mainElement = element;
                            break;
                        }
                    }
                    
                    // Fallback to body
                    const targetElement = mainElement || document.body;
                    
                    // Get clean text - no HTML, no corruption
                    return targetElement.innerText || targetElement.textContent || '';
                }''')
                
                await browser.close()
                
                if content and len(content) > 100:
                    # Check if this is a 404 or not found page
                    if self._is_404_or_not_found(content):
                        print(f"    🚫 Playwright detected 404/Not Found page, skipping...")
                        return None
                    
                    # If content looks too short (likely blocked), try multiple fallbacks
                    if len(content) < 600:
                        print(f"    ⚠️ Playwright content short ({len(content)} chars), trying fallbacks...")
                        
                        # Try requests fallback first
                        req_text = self._get_page_content_requests(url)
                        if req_text and len(req_text) > 600:
                            print(f"    ✅ Requests fallback extracted {len(req_text)} chars")
                            return req_text[:10000]
                        
                        # For Walmart specifically, try different approach
                        if 'walmart.com' in url:
                            print(f"    🔄 Walmart detected, trying alternative extraction...")
                            # Try without waiting for networkidle (faster load)
                            try:
                                alt_page = await context.new_page()
                                await alt_page.goto(url, timeout=20000, wait_until='domcontentloaded')
                                await alt_page.wait_for_timeout(1000)
                                alt_content = await alt_page.evaluate('() => document.body.innerText || document.body.textContent || ""')
                                await alt_page.close()
                                if alt_content and len(alt_content) > len(content):
                                    print(f"    ✅ Alternative extraction got {len(alt_content)} chars")
                                    return alt_content[:10000]
                            except:
                                pass
                        
                        print(f"    ⚠️ All fallbacks short, using best available ({len(content)} chars)")
                        return content[:10000]

                    print(f"    ✅ Playwright extracted {len(content)} chars")
                    return content[:10000]
                else:
                    print(f"    ⚠️ Playwright content too short: {len(content) if content else 0} chars")
                    return None
                
        except Exception as e:
            print(f"    ❌ Playwright error: {e}")
            return None

    def _is_404_or_not_found(self, text: str, response_code: int = 200) -> bool:
        """Detect if page is 404, not found, or has no useful content"""
        if not text or len(text.strip()) < 50:
            return True
            
        # Check HTTP status codes
        if response_code >= 400:
            return True
            
        text_lower = text.lower()
        
        # Common 404/not found indicators
        not_found_indicators = [
            "this page couldn't be found",
            "page not found", "404", "not found",
            "page doesn't exist", "page does not exist",
            "sorry, we can't find that page",
            "the page you're looking for doesn't exist",
            "oops! page not found",
            "we couldn't find the page you were looking for",
            "the requested page could not be found",
            "error 404", "http 404",
            "sorry about that!", "return to home"
        ]
        
        # Check if text contains multiple not found indicators
        found_indicators = sum(1 for indicator in not_found_indicators if indicator in text_lower)
        
        # If multiple indicators or very short content, it's likely a 404
        if found_indicators >= 2 or (found_indicators >= 1 and len(text.strip()) < 200):
            return True
            
        return False

    def _get_page_content_requests(self, url: str) -> Optional[str]:
        """Get page content using requests + BeautifulSoup"""
        try:
            print(f"  📥 Fetching {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # SIMPLE AND EFFECTIVE cleaning (like the working version)
            import re
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content area
            main_content = None
            content_selectors = [
                'main', '[role="main"]', '.main-content', '.content',
                '.policy-content', '.page-content', '.rte', '.shopify-policy__container',
                'article', '.article', '[class*="policy"]', '[class*="shipping"]', '[class*="return"]'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 200:
                        main_content = element
                        break
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.body or soup
            
            # Extract text (SIMPLE approach like working version)
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean text (SIMPLE like working version)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Check if this is a 404 or not found page
            if self._is_404_or_not_found(text, response.status_code):
                print(f"  🚫 Detected 404/Not Found page, skipping...")
                return None
            
            if len(text) > 50:
                print(f"  ✅ Extracted {len(text)} chars")
                return text[:10000]  # Limit for performance
            else:
                print(f"  ⚠️ Content too short: {len(text)} chars")
                return None
                
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return None
    
    async def _advanced_crawler_fallback(self, domain: str) -> List[str]:
        """Advanced crawler fallback using CompleteCrawler for difficult sites"""
        try:
            # Import the complete crawler
            from complete_crawler import CompleteCrawler
            
            print(f"  🕷️ Running advanced crawler on {domain}...")
            crawler = CompleteCrawler(domain, max_pages=50)  # Limit for speed
            
            # Run the complete crawler
            policy_urls = await crawler.run_complete_crawl()
            
            print(f"  ✅ Advanced crawler found {len(policy_urls)} URLs")
            
            # Return top scored URLs
            return policy_urls[:15]  # Top 15
            
        except Exception as e:
            print(f"  ❌ Advanced crawler error: {e}")
            return []
    
    async def _get_manual_policy_urls(self, domain: str) -> List[str]:
        """SMART manual fallback with US-focused active URL testing for difficult sites like Zara."""
        active_urls = []
        
        # PRIORITY 1: UNIVERSAL US patterns (works for ALL e-commerce sites)
        us_priority_patterns = [
            # UNIVERSAL: All possible US locale combinations with .html extensions
            "/en_us/customer-service/returns.html",    # H&M, Gap, etc.
            "/en_us/customer-service/shipping.html", 
            "/en_us/customer-service/delivery.html",
            "/en_us/help/returns.html",               # Many retail sites
            "/en_us/help/shipping.html",
            "/en_us/help/delivery.html",
            "/en_us/support/returns.html",            # Tech/fashion sites
            "/en_us/support/shipping.html",
            "/en_us/faq/returns.html",                # FAQ-based sites
            "/en_us/faq/shipping.html",
            
            # UNIVERSAL: Same patterns WITHOUT .html
            "/en_us/customer-service/returns",
            "/en_us/customer-service/shipping",
            "/en_us/help/returns",
            "/en_us/help/shipping",
            "/en_us/support/returns", 
            "/en_us/support/shipping",
            "/en_us/faq/returns",
            "/en_us/faq/shipping",
            
            # UNIVERSAL: Dash format (us-en) with .html
            "/us-en/customer-service/returns.html",   # Some international sites
            "/us-en/customer-service/shipping.html",
            "/us-en/help/returns.html",
            "/us-en/help/shipping.html",
            
            # UNIVERSAL: Standard US patterns (us/en) 
            "/us/en/help/shipping-and-returns",       # Zara, luxury brands
            "/us/en/help/returns", 
            "/us/en/help/shipping",
            "/us/en/customer-service/shipping",
            "/us/en/customer-service/returns",
            "/us/en/help-center/shipping",
            "/us/en/help-center/returns",
            "/us/en/help-center/delivery",
            "/us/en/support/returns",
            "/us/en/support/shipping",
            
            # UNIVERSAL: Reverse format (en-us)
            "/en-us/help/shipping-and-returns",       # Microsoft, tech sites
            "/en-us/help/returns",
            "/en-us/help/shipping", 
            "/en-us/customer-service/shipping",
            "/en-us/customer-service/returns",
            "/en-us/support/returns",
            "/en-us/support/shipping",
        ]
        
        # PRIORITY 2: Common retail patterns 
        retail_patterns = [
            "/customer-service/shipping",
            "/customer-service/returns",
            "/help/shipping-and-returns",
            "/help/returns",
            "/help/shipping", 
            "/help/delivery",
            "/support/shipping",
            "/support/returns",
            "/shipping-and-returns",
            "/returns-and-exchanges",
            "/shipping-returns",
            "/delivery-returns",
        ]
        
        # PRIORITY 3: Generic help pages
        generic_patterns = [
            "/help",
            "/customer-service", 
            "/support",
            "/faq",
            "/help-center"
        ]
        
        all_patterns = us_priority_patterns + retail_patterns + generic_patterns
        print(f"  🎯 Smart testing {len(all_patterns)} US-focused URL patterns...")
        
        # Test URLs in batches and check if they're active
        tested_count = 0
        found_count = 0
        
        for pattern in all_patterns:
            test_url = f"https://{domain}{pattern}"
            
            # Quick HEAD request to check if URL is active
            try:
                response = self.session.head(test_url, timeout=3, allow_redirects=True)
                if response.status_code < 400:
                    active_urls.append(test_url)
                    found_count += 1
                    print(f"    ✅ Active: {test_url} ({response.status_code})")
                    
                    # Stop early if we found enough good URLs
                    if found_count >= 15:  # Limit to best 15 URLs
                        break
                else:
                    print(f"    ❌ Dead: {test_url} ({response.status_code})")
                    
            except Exception as e:
                print(f"    ⚠️ Error: {test_url} ({str(e)[:50]})")
            
            tested_count += 1
            
            # Don't test forever
            if tested_count >= 30:
                break
        
        print(f"  🎯 Found {found_count} active US URLs from {tested_count} tested")
        
        # If we didn't find enough, add some untested high-probability ones
        if len(active_urls) < 5:
            print("  🔄 Adding high-probability backup URLs...")
            backup_urls = [
                f"https://{domain}/us/en/help",
                f"https://{domain}/help-center",
                f"https://{domain}/customer-service",
                f"https://{domain}/help",
                f"https://{domain}/support"
            ]
            active_urls.extend(backup_urls)
        
        return active_urls
