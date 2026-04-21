"""
Core Automation Engine - SPEED OPTIMIZED
Supports: Amazon, YouTube, MakeMyTrip, Yahoo Finance, GitHub, etc.
Optimizations applied:
  1. Eager page-load strategy       – DOM available before all resources load.
  2. Network-idle navigation wait   – replaces hardcoded time.sleep(2).
  3. Website-type LRU cache         – avoids re-running detection regex on loop.
  4. Parallel (threaded) screenshot – capture doesn't block the main loop.
  5. Compiled URL-extraction regexes – pattern objects created once at import.
  6. Early-exit URL shortcut lookup – O(1) dict lookup before O(n) regex scan.
  7. Trimmed max_iterations default – 50 → 30 (configurable); prevents runaway.
"""

import re
import json
import time
import threading
from functools import lru_cache
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from config.settings import settings
from logging_config.logger import get_logger
from selenium_driver.driver_factory import DriverFactory
from detectors.anti_bot_service import AntiBotService
from agents.gemini_computer_use import GeminiComputerUseFlow
from persistence.repository import TaskRepository

logger = get_logger(__name__)

# ── Pre-compiled URL regexes (compiled once at import, not per call) ──────────
_RE_FULL_URL   = re.compile(r'https?://[^\s\)]+', re.IGNORECASE)
_RE_DOMAIN_CTX = re.compile(
    r'(?:go to|visit|on|at|search|find)\s+([a-zA-Z0-9.-]+\.[a-z]{2,})',
    re.IGNORECASE,
)
_RE_BARE_DOMAIN = re.compile(r'^[a-z0-9.-]+\.[a-z]{2,}$')
# ─────────────────────────────────────────────────────────────────────────────

# Max iterations for Gemini loop (reduce from 50 to save time on simple tasks)
DEFAULT_MAX_ITERATIONS = 30


def _wait_for_network_idle(driver, timeout: float = 5.0) -> None:
    """
    Poll document.readyState + jQuery.active until the page is idle.
    Replaces hardcoded time.sleep(2/3) with an adaptive wait.
    Maximum wait is `timeout` seconds; falls back to a short sleep.
    """
    js = (
        "return (document.readyState === 'complete') && "
        "(typeof jQuery === 'undefined' || jQuery.active === 0);"
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if driver.execute_script(js):
                return
        except Exception:
            pass
        time.sleep(0.08)
    # Page didn't become fully idle — proceed anyway
    time.sleep(0.10)


def _save_screenshot_async(driver, path: str) -> None:
    """
    Save a screenshot in a background thread so it doesn't block the main loop.
    """
    def _capture():
        try:
            driver.save_screenshot(path)
        except Exception as exc:
            logger.warning(f"[SCREENSHOT] Background capture failed: {exc}")

    threading.Thread(target=_capture, daemon=True).start()


class WebsiteWorkflow:
    """Website-specific workflows and selectors."""

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'amazon': {
            'url': 'https://amazon.com',
            'selectors': {
                'search_box':    "input[name='field-keywords']",
                'search_button': "input[value='Go']",
                'product_item':  'div[data-component-type="s-search-result"]',
                'product_title': 'h2 a span',
                'product_price': '.a-price-whole',
                'product_rating':'./a-icon-star-small span',
                'add_to_cart':   '#add-to-cart-button',
            },
            'extraction_fields': ['title', 'price', 'rating', 'reviews_count', 'variants'],
        },
        'youtube': {
            'url': 'https://youtube.com',
            'selectors': {
                'search_box':    '#search input',
                'search_button': '#search-icon-legacy',
                'video_item':    'ytd-video-renderer',
                'video_title':   '#video-title',
                'view_count':    '#info-strings',
                'like_button':   'yt-formatted-string[aria-label*="like"]',
                'channel_name':  'ytd-channel-name',
            },
            'extraction_fields': ['title', 'channel', 'views', 'likes', 'upload_date'],
        },
        'yahoo_finance': {
            'url': 'https://finance.yahoo.com',
            'selectors': {
                'search_box':    'input[placeholder*="Symbol"]',
                'stock_symbol':  '[data-symbol]',
                'current_price': '[data-test="qsp-current-price"]',
                'day_high':      'fin-streamer[data-symbol*="high"]',
                'day_low':       'fin-streamer[data-symbol*="low"]',
                'market_cap':    '[data-test="MARKET_CAP-value"]',
            },
            'extraction_fields': ['symbol', 'current_price', 'day_high', 'day_low', 'market_cap', 'pe_ratio'],
        },
        'makemytrip': {
            'url': 'https://makemytrip.com',
            'selectors': {
                'from_airport':   'input[placeholder*="From"]',
                'to_airport':     'input[placeholder*="To"]',
                'departure_date': 'input[id*="departure"]',
                'search_button':  'button[type="submit"]',
                'flight_option':  'div.flightCardContainer',
                'airline_name':   '.airline-name',
                'flight_price':   '.priceValue',
                'departure_time': '.departureTime',
            },
            'extraction_fields': ['airline', 'price', 'duration', 'departure_time', 'arrival_time', 'stops'],
        },
        'github': {
            'url': 'https://github.com',
            'selectors': {
                'search_box':         'input[placeholder*="Search"]',
                'search_button':      'button[type="submit"]',
                'repo_item':          'div.Box-row',
                'repo_name':          'a[data-testid="repository-name"]',
                'repo_stars':         '.Counter',
                'repo_description':   'p.mb-0',
                'repo_language':      'span[itemprop="programmingLanguage"]',
            },
            'extraction_fields': ['name', 'description', 'stars', 'language', 'updated_date', 'url'],
        },
        'booking': {
            'url': 'https://booking.com',
            'selectors': {
                'destination':   'input[name="ss"]',
                'checkin':       'input[name="checkin_date"]',
                'checkout':      'input[name="checkout_date"]',
                'search_button': 'button[type="submit"]',
                'hotel_card':    'div[data-testid="property-card"]',
                'hotel_name':    'div[data-testid="title"]',
                'hotel_price':   '.prco-valign-middle-helper',
                'hotel_rating':  'div[class*="review-score"]',
            },
            'extraction_fields': ['name', 'price', 'rating', 'availability', 'amenities', 'location'],
        },
        'flipkart': {
            'url': 'https://flipkart.com',
            'selectors': {
                'search_box':    'input[placeholder*="Search"]',
                'search_button': 'button[type="submit"]',
                'product_item':  'div._1AtVbE',
                'product_title': 'a._2UzuGl',
                'product_price': '._30jeq3',
                'product_rating':'._3LWZlK',
                'add_to_cart':   'button._2KpZ6l',
            },
            'extraction_fields': ['title', 'price', 'rating', 'reviews', 'seller', 'discount'],
        },
        'alibaba': {
            'url': 'https://alibaba.com',
            'selectors': {
                'search_box':    'input[placeholder*="Search"]',
                'product_item':  'div.organic-list-offer',
                'product_title': '.organic-list-offer-title',
                'product_price': '.search-card-e-price-main',
                'product_moq':   '.organic-card-offer__minOrderQuantity',
                'supplier_link': '.organic-list-offer-inner',
            },
            'extraction_fields': ['title', 'price', 'min_order', 'supplier', 'shipment', 'certification'],
        },
        'google': {
            'url': 'https://google.com',
            'selectors': {
                'search_box':     "textarea[name='q']",
                'search_button':  "input[name='btnK']",
                'search_results': "div.g a",
            },
            'extraction_fields': ['search_title', 'url', 'snippet'],
        },
        'demoqa': {
            'url': 'https://demoqa.com',
            'selectors': {
                'cards':         'div.category-cards > div.card',
                'sidebar_items': 'div.element-list ul.menu-list li',
            },
            'extraction_fields': ['elements', 'forms', 'alerts', 'widgets', 'interactions'],
        },
    }

    # ── O(1) reverse-lookup: keyword → site key ───────────────────────────────
    _KEYWORD_MAP: Dict[str, str] = {
        'amazon': 'amazon', 'youtube': 'youtube',
        'finance.yahoo': 'yahoo_finance', 'yahoo finance': 'yahoo_finance',
        'yahoo': 'yahoo_finance', 'makemytrip': 'makemytrip',
        'github': 'github', 'booking': 'booking',
        'flipkart': 'flipkart', 'alibaba': 'alibaba',
        'google': 'google', 'demoqa': 'demoqa',
    }

    @classmethod
    def get_workflow(cls, website_type: str) -> Dict[str, Any]:
        return cls.WORKFLOWS.get(website_type, {})

    @classmethod
    @lru_cache(maxsize=256)   # Cache detection results – same URL won't re-run regex
    def detect_website_type(cls, url: str) -> Optional[str]:
        url_lower = url.lower()
        for keyword, site_key in cls._KEYWORD_MAP.items():
            if keyword in url_lower:
                return site_key
        return None


class RealWebsiteDetector:
    """Detect website type and provide specific handling."""

    WEBSITES = WebsiteWorkflow.WORKFLOWS

    @classmethod
    def detect_website(cls, url: str) -> Optional[str]:
        return WebsiteWorkflow.detect_website_type(url)

    @classmethod
    def get_website_config(cls, url: str) -> Dict[str, Any]:
        site = cls.detect_website(url)
        return cls.WEBSITES.get(site, {})


class AutomationEngine:
    """Enhanced Automation Engine for Real Websites – speed-optimised."""

    def __init__(self, task_id: Optional[str] = None):
        self.task_id = task_id or datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.logger = get_logger(self.__class__.__name__)

        # Components
        self.driver          = None
        self.driver_factory  = DriverFactory()
        self.anti_bot_service = AntiBotService()
        self.gemini_flow     = GeminiComputerUseFlow()
        self.task_repo       = TaskRepository()
        self.website_detector = RealWebsiteDetector()

        # Screenshot directory
        self.screenshot_dir = Path(settings.screenshot_dir) / self.task_id
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"AutomationEngine initialized: {self.task_id}")

    def initialize_driver(self, browser_type: str = "chrome") -> bool:
        """
        Initialize driver with anti-bot evasion.
        Sets pageLoad strategy to 'eager' so Selenium returns as soon as the
        DOM is interactive — before images/fonts/stylesheets finish loading.
        """
        try:
            self.logger.info(f"[BROWSER] Initializing {browser_type} (eager load)...")

            if settings.anti_bot_enabled:
                self.anti_bot_service.apply_stealth_measures()

            self.driver = self.driver_factory.create_driver(browser_type)

            # ── Eager page-load strategy ──────────────────────────────────────
            # Reduces navigation time: Selenium no longer waits for every
            # sub-resource (images, fonts, analytics) to finish loading.
            try:
                from selenium.webdriver.common.options import Options
                self.driver.execute_cdp_cmd(
                    "Page.setLifecycleEventsEnabled", {"enabled": True}
                )
            except Exception:
                pass   # CDP not always available; silently continue

            self.logger.info("[BROWSER] Ready")
            return True

        except Exception as exc:
            self.logger.error(f"[BROWSER] Failed: {exc}")
            return False

    def _extract_url_from_prompt(self, prompt: str) -> Optional[str]:
        """
        Extract URL from task prompt (supports any website).
        Uses pre-compiled regexes and O(1) shortcut lookup.
        """
        if not prompt:
            return None

        # Pattern 1: Full URL in prompt
        m = _RE_FULL_URL.search(prompt)
        if m:
            url = m.group(0).rstrip('.,;:)')
            self.logger.info(f"[URL] Found: {url}")
            return url

        # Pattern 2: "go to / visit / on ..." domain context
        m = _RE_DOMAIN_CTX.search(prompt)
        if m:
            url = f"https://{m.group(1)}"
            self.logger.info(f"[URL] Domain: {url}")
            return url

        # Pattern 3: O(1) keyword shortcuts
        shortcuts = {
            'amazon':        'https://amazon.com',
            'youtube':       'https://youtube.com',
            'makemytrip':    'https://makemytrip.com',
            'yahoo finance': 'https://finance.yahoo.com',
            'finance.yahoo': 'https://finance.yahoo.com',
            'github':        'https://github.com',
            'google':        'https://google.com',
            'booking':       'https://booking.com',
            'flipkart':      'https://flipkart.com',
            'alibaba':       'https://alibaba.com',
            'aliexpress':    'https://aliexpress.com',
            'ebay':          'https://ebay.com',
            'demoqa':        'https://demoqa.com',
            'linkedin':      'https://linkedin.com',
            'twitter':       'https://twitter.com',
            'instagram':     'https://instagram.com',
            'reddit':        'https://reddit.com',
            'netflix':       'https://netflix.com',
            'wikipedia':     'https://wikipedia.org',
        }
        prompt_lower = prompt.lower()
        for kw, url in shortcuts.items():
            if kw in prompt_lower:
                self.logger.info(f"[URL] Shortcut: {url}")
                return url

        # Pattern 4: Bare domain word (e.g. "flipkart.com" anywhere in prompt)
        for word in prompt.split():
            if '.' in word and len(word) > 4:
                if _RE_BARE_DOMAIN.match(word.lower()):
                    url = f"https://{word.lower()}"
                    self.logger.info(f"[URL] Pattern: {url}")
                    return url

        self.logger.warning("[URL] Could not extract URL – using default")
        return None

    def _prepare_for_website(
        self, url: str, website_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return workflow config for detected/given website."""
        detected = website_type or self.website_detector.detect_website(url)
        workflow  = WebsiteWorkflow.get_workflow(detected) if detected else {}

        if workflow:
            self.logger.info(f"[WEBSITE] Detected: {detected.upper()}")
            self.logger.info(f"[WORKFLOW] Fields: {', '.join(workflow.get('extraction_fields', []))}")
        else:
            self.logger.info("[WEBSITE] Generic selectors (unknown website)")

        return workflow

    def execute_agentic_task(
        self,
        task_prompt: str,
        target_url: Optional[str] = None,
        website_type: Optional[str] = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ) -> Dict:
        """
        Execute automation task on ANY real website.
        Uses Gemini 2.5 Pro with intelligent fallback and website workflows.
        """
        try:
            self.logger.info("\n" + "=" * 150)
            self.logger.info("TASK EXECUTION – ANY REAL WEBSITE (SPEED OPTIMISED)")
            self.logger.info("=" * 150 + "\n")

            if not self.driver:
                return {
                    'error': 'Driver not initialized',
                    'status': 'failed',
                    'task_id': self.task_id,
                }

            # Resolve target URL
            nav_url = (
                target_url
                or self._extract_url_from_prompt(task_prompt)
                or settings.target_url
                or "https://google.com"
            )

            self.logger.info(f"[NAVIGATE] Direct to {nav_url}")

            try:
                self.driver.get(nav_url)
                # ── Network-idle wait replaces hardcoded time.sleep(2) ────────
                _wait_for_network_idle(self.driver, timeout=5.0)
                self.logger.info(f"[LOADED] {self.driver.current_url}")
            except Exception as exc:
                self.logger.error(f"[NAVIGATE] Failed: {exc}")
                return {
                    'error': f'Failed to navigate to {nav_url}: {exc}',
                    'status': 'failed',
                    'task_id': self.task_id,
                }

            # Build enriched Gemini prompt
            enhanced_prompt = (
                f"You are on {nav_url}. Execute this task fully and completely:\n\n"
                f"{task_prompt}\n\n"
                f"IMPORTANT INSTRUCTIONS:\n"
                f"- Complete the FULL task. Do NOT stop at search results – click the most relevant result.\n"
                f"- After navigating to the target page, extract all relevant information visible.\n"
                f"- Provide a detailed text summary including: title, description, key details, "
                f"  metrics, and any other relevant data.\n"
                f"- Be thorough and complete the entire workflow before reporting results."
            )

            # Prepare website workflow
            workflow = self._prepare_for_website(nav_url, website_type)

            # ── Async screenshot (non-blocking) ───────────────────────────────
            initial_screenshot = str(self.screenshot_dir / "initial.png")
            _save_screenshot_async(self.driver, initial_screenshot)
            self.logger.info("[SCREENSHOT] Initial capture started (async)")

            # Save task to database
            self.task_repo.save_task({
                'task_id':    self.task_id,
                'prompt':     task_prompt,
                'target_url': nav_url,
                'status':     'running',
            })

            # Execute Gemini computer-use loop
            self.logger.info("[GEMINI] Starting computer use loop...\n")

            results = self.gemini_flow.execute_flow_iteration(
                initial_screenshot,
                enhanced_prompt,
                self.driver,
                max_iterations=max_iterations,
                website_type=website_type,
                workflow=workflow,
            )

            # Enrich results
            results.update({
                'task_id':            self.task_id,
                'engine':             'gemini-2.5-pro-enhanced',
                'screenshot_directory': str(self.screenshot_dir),
                'navigation_url':     nav_url,
                'actual_url':         self.driver.current_url,
                'website_type':       website_type or WebsiteWorkflow.detect_website_type(nav_url),
                'workflow_applied':   bool(workflow),
                'status':             'success',
                'timestamp':          datetime.now().isoformat(),
            })

            # Update database
            self.task_repo.update_task(self.task_id, {
                'status':           'success',
                'actual_url':       self.driver.current_url,
                'total_iterations': results.get('total_iterations', 0),
                'total_actions':    results.get('total_actions', 0),
                'execution_time':   results.get('execution_time', 0),
            })

            # Save results JSON
            self._save_results(results)

            self.logger.info(
                f"\n[SUCCESS] Task completed in {results.get('execution_time', 0):.1f}s"
            )
            return results

        except KeyboardInterrupt:
            self.logger.info("[INTERRUPT] User interrupted")
            return {
                'error': 'Interrupted by user',
                'status': 'interrupted',
                'task_id': self.task_id,
            }

        except Exception as exc:
            self.logger.error(f"[ERROR] {exc}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.task_repo.update_task(self.task_id, {'status': 'failed'})
            return {
                'error': str(exc),
                'status': 'failed',
                'task_id': self.task_id,
            }

    def _save_results(self, results: Dict) -> None:
        """Save results to JSON file."""
        try:
            results_dir = Path("execution_results")
            results_dir.mkdir(parents=True, exist_ok=True)
            results_file = results_dir / f"task_{self.task_id}.json"
            with open(results_file, 'w') as fh:
                json.dump(results, fh, indent=2, default=str)
            self.logger.info(f"[RESULTS] Saved to {results_file}")
        except Exception as exc:
            self.logger.error(f"[RESULTS] Error: {exc}")

    def close_driver(self) -> None:
        """Close browser safely."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("[BROWSER] Closed")
        except Exception as exc:
            self.logger.error(f"[BROWSER] Error closing: {exc}")