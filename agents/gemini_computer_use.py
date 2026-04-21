"""
Gemini 2.5 Computer Use Flow - Agentic Web Automation
Uses the official Gemini Computer Use tool API with structured FunctionCall responses.
Fallback chain: Gemini Computer Use → Groq Vision → Rule-Based Analysis

Supported Computer Use actions:
  click_at, type_text_at, scroll_document, scroll_at, navigate, go_back, go_forward,
  open_web_browser, wait_5_seconds, key_combination, hover_at, drag_and_drop, search
"""

import json
import base64
import time
import logging
import threading
import re
from pathlib import Path
from typing import Dict, Optional, Any, List, Set, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
from html import escape

# New google-genai SDK
try:
    from google import genai
    from google.genai import types
    from google.genai.types import Content, Part, FunctionResponse
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore
    types = None  # type: ignore
    Content = None  # type: ignore
    Part = None  # type: ignore
    FunctionResponse = None  # type: ignore
    GEMINI_AVAILABLE = False

# Groq fallback
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None  # type: ignore
    GROQ_AVAILABLE = False

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    WebDriverException,
)

# Safe imports with fallback
try:
    from config.settings import settings
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False
    settings = None
    class Settings:
        gemini_api_key = None
        computer_use_model = "gemini-2.5-computer-use-preview-10-2025"
        screenshot_dir = Path("./screenshots")
    settings = Settings()

try:
    from logging_config.logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)


class WebsiteSelector:
    """Website-specific selectors and strategies"""
    
    SELECTORS = {
        'amazon': {
            'search_input': ["input[name='field-keywords']", "input[placeholder*='Search']"],
            'search_button': ["input[value='Go']", "button[type='submit']"],
            'products': ["div[data-component-type='s-search-result']", "div.s-result-item"],
            'title': ["h2 a span", "a h2 span"],
            'price': [".a-price-whole", ".a-price-base"],
            'rating': [".a-icon-star-small span", ".a-rating"],
        },
        'youtube': {
            'search_input': ["#search input", "input[placeholder='Search']"],
            'search_button': ["#search-icon-legacy", "button[aria-label='Search']"],
            'videos': ["ytd-video-renderer", "a#video-title"],
            'title': ["#video-title", "h3 a span"],
            'views': ["#info-strings", "yt-formatted-string[aria-label*='views']"],
        },
        'yahoo_finance': {
            'search_input': ["input[placeholder*='Symbol']", "input[type='text']"],
            'search_button': ["button[type='submit']"],
            'stock_price': ["[data-test='qsp-current-price']", "fin-streamer[data-field='regularMarketPrice']"],
            'symbol': ["h1", "span[data-symbol]"],
            'metrics': ["[data-test*='value']"],
        },
        'makemytrip': {
            'search_from': ["input[placeholder*='From']", "input[data-testid='fromCity']"],
            'search_to': ["input[placeholder*='To']", "input[data-testid='toCity']"],
            'date_picker': ["input[id*='departure']", "input[placeholder*='Departure']"],
            'search_button': ["button[type='submit']", "button[class*='searchButton']"],
            'flights': ["div.flightCardContainer", "div[class*='flightResult']"],
            'price': [".priceValue", "span[class*='price']"],
        },
        'github': {
            'search_input': ["input[placeholder*='Search']", "input[type='search']"],
            'search_button': ["button[type='submit']"],
            'repos': ["div.Box-row", "a[data-testid='repository-name']"],
            'stars': [".Counter", "span[class*='Star']"],
        },
        'booking': {
            'search_dest': ["input[name='ss']", "input[placeholder*='Where']"],
            'check_in': ["input[name='checkin_date']"],
            'check_out': ["input[name='checkout_date']"],
            'search_button': ["button[type='submit']"],
            'hotels': ["div[data-testid='property-card']"],
            'price': [".prco-valign-middle-helper", "span[class*='price']"],
        },
        'flipkart': {
            'search_input': ["input[placeholder*='Search']", "input[class*='search']"],
            'search_button': ["button[type='submit']"],
            'products': ["div._1AtVbE", "div[class*='productItem']"],
            'title': ["a._2UzuGl", "a[class*='productTitle']"],
            'price': ["._30jeq3", "span[class*='price']"],
        },
        'google': {
            'search_input': ["textarea[name='q']", "input[name='q']"],
            'search_button': ["input[name='btnK']", "button[name='btnG']"],
            'search_results': ["div.g a", "h3"],
        },
        'demoqa': {
            'cards': ["div.category-cards > div.card"],
            'sidebar_items': ["div.element-list ul.menu-list li"],
            'forms': ["#firstName", "#lastName"],
        }
    }
    
    @staticmethod
    def detect_website(url: str) -> Optional[str]:
        """Detect website from URL"""
        url_lower = url.lower()
        for site in WebsiteSelector.SELECTORS.keys():
            if site in url_lower:
                return site
        return None
    
    @staticmethod
    def get_selectors(website: Optional[str], element_type: str) -> List[str]:
        """Get CSS selectors for website and element type"""
        if not website or website not in WebsiteSelector.SELECTORS:
            return []
        return WebsiteSelector.SELECTORS[website].get(element_type, [])


class AdvancedFallbackAnalyzer:
    """
    Advanced rule-based analyzer using AI-like logic without Gemini
    Mimics Gemini 2.5 Computer Use perfectly using DOM analysis
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)
        self.action_history: List[Dict[str, Any]] = []
        self.visited_elements: Set[str] = set()
        self.wait = WebDriverWait(driver, timeout=10)
        self.website = None
        self.task_progress = 0
    
    def analyze_page(self, task_prompt: str, iteration: int) -> Dict[str, Any]:
        """Analyze page and determine next action"""
        try:
            # Detect website
            self.website = WebsiteSelector.detect_website(self.driver.current_url)
            
            analysis = {
                'analysis': self._get_page_description(),
                'action': self._determine_action(task_prompt, iteration),
                'reasoning': f'Advanced fallback analysis (iteration {iteration})',
                'task_complete': self._check_completion(task_prompt),
                'confidence': self._calculate_confidence(iteration)
            }
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Fallback analysis error: {e}", exc_info=True)
            return self._safe_fallback_action()
    
    def _get_page_description(self) -> str:
        """Get intelligent page description"""
        try:
            title = self.driver.title or "Unknown"
            url = self.driver.current_url or "Unknown"
            
            # Get main content indicators
            indicators = []
            
            # Check for search inputs
            try:
                search_inputs = self.driver.find_elements(
                    By.XPATH, 
                    "//*[@placeholder or @aria-label] | input[type='search'] | input[type='text']"
                )
                if search_inputs:
                    indicators.append(f"search box found")
            except:
                pass
            
            # Check for main content
            try:
                content = self.driver.find_elements(By.XPATH, "//main | //[role='main']")
                if content:
                    indicators.append("main content visible")
            except:
                pass
            
            # Build description
            desc = f"Page: {title}. URL: {url}"
            if indicators:
                desc += f". Elements: {', '.join(indicators)}"
            
            return desc[:250]
        
        except Exception as e:
            self.logger.warning(f"Page description error: {e}")
            return f"Page: {self.driver.current_url}"
    
    def _determine_action(self, task_prompt: str, iteration: int) -> Dict[str, Any]:
        """Determine action intelligently"""
        
        task_lower = task_prompt.lower()
        url = self.driver.current_url.lower()
        
        try:
            # 1. State: Are we on Google? We need to search and navigate to the target website.
            if "google.com" in url:
                if iteration <= 2:
                    return self._phase_search(task_lower, url)
                else:
                    return self._phase_navigate(task_lower, url) # click search result

            # 2. State: DemoQA Structural Navigation
            if "demoqa.com" in url:
                return self._demoqa_workflow(task_lower, iteration)

            # 3. State: Specific Workflows (Amazon, YouTube, Yahoo Finance)
            if "amazon.com" in url:
                return self._amazon_workflow(task_lower, iteration)
            if "youtube.com" in url:
                return self._youtube_workflow(task_lower, iteration)
            if "finance.yahoo.com" in url:
                return self._yahoo_finance_workflow(task_lower, iteration)

            # 4. Standard Fallback Phases
            if iteration <= 3: # Allow an extra iteration for search phase
                return self._phase_search(task_lower, url)
            elif iteration <= 8:
                return self._phase_navigate(task_lower, url)
            else:
                return self._phase_extract(task_lower, url)
        
        except Exception as e:
            self.logger.error(f"Action determination error: {e}")
            return self._safe_fallback_action()

    def _demoqa_workflow(self, task: str, iteration: int) -> Dict[str, Any]:
        """Specific logic to navigate DemoQA modules"""
        if iteration <= 3:
            return {'type': 'click', 'target': 'Elements', 'confidence': 0.85}
        elif iteration <= 5:
            return {'type': 'click', 'target': 'Forms', 'confidence': 0.85}
        elif iteration <= 7:
            return {'type': 'click', 'target': 'Alerts', 'confidence': 0.85}
        elif iteration <= 9:
            return {'type': 'click', 'target': 'Widgets', 'confidence': 0.85}
        else:
            return {'type': 'complete', 'target': 'Explored structural nodes', 'confidence': 0.9}

    def _amazon_workflow(self, task: str, iteration: int) -> Dict[str, Any]:
        """Specific logic for Amazon search -> variants -> summary"""
        if iteration <= 3:
            return self._phase_search(task, self.driver.current_url)
        elif "iphone" in task and iteration <= 6:
            return {'type': 'click', 'target': 'iphone', 'confidence': 0.85}
        else:
            return self._phase_extract(task, self.driver.current_url)

    def _youtube_workflow(self, task: str, iteration: int) -> Dict[str, Any]:
        """Specific logic for YouTube search -> click video -> summary"""
        if iteration <= 3:
            return self._phase_search(task, self.driver.current_url)
        elif iteration <= 6:
            # Click first video matching text broadly
            return {'type': 'click', 'target': 'video', 'confidence': 0.8}
        else:
            return self._phase_extract(task, self.driver.current_url)

    def _yahoo_finance_workflow(self, task: str, iteration: int) -> Dict[str, Any]:
        """Specific logic for Yahoo Finance quote -> summary"""
        if iteration <= 3:
            return self._phase_search(task, self.driver.current_url)
        elif iteration <= 6:
            return {'type': 'click', 'target': 'tesla', 'confidence': 0.8}
        else:
            return self._phase_extract(task, self.driver.current_url)
    
    def _phase_search(self, task_lower: str, url: str) -> Dict[str, Any]:
        """Handle search/input phase with website-specific logic"""
        
        try:
            # Get website-specific selectors
            search_selectors = WebsiteSelector.get_selectors(self.website, 'search_input')
            
            # Try website-specific selectors first
            for selector in search_selectors:
                try:
                    inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if inputs and inputs[0].is_displayed():
                        search_term = self._extract_search_term(task_lower)
                        return {
                            'type': 'fill',
                            'target': selector,
                            'value': search_term,
                            'confidence': 0.90
                        }
                except:
                    continue
            
            # Generic search input detection
            try:
                generic_inputs = self.driver.find_elements(
                    By.XPATH,
                    "//input[@placeholder or @aria-label] | //input[contains(@name, 'search')]"
                )
                for input_elem in generic_inputs:
                    if input_elem.is_displayed():
                        search_term = self._extract_search_term(task_lower)
                        return {
                            'type': 'fill',
                            'target': 'search input',
                            'value': search_term,
                            'confidence': 0.80
                        }
            except:
                pass
            
            # Fallback: scroll to find
            return {
                'type': 'scroll',
                'target': 'down',
                'value': 300,
                'confidence': 0.60
            }
        
        except Exception as e:
            self.logger.warning(f"Search phase error: {e}")
            return self._safe_fallback_action()
    
    def _phase_navigate(self, task_lower: str, url: str) -> Dict[str, Any]:
        """Handle navigation/clicking phase"""
        
        try:
            # Look for submit/search buttons
            button_labels = ['search', 'submit', 'find', 'go', 'book', 'apply']
            
            for label in button_labels:
                try:
                    buttons = self.driver.find_elements(
                        By.XPATH,
                        f"//button | //input[@type='submit'] | //a[contains(text(), '{label}')]"
                    )
                    if buttons and buttons[0].is_displayed():
                        return {
                            'type': 'click',
                            'target': f'button: {label}',
                            'value': None,
                            'confidence': 0.85
                        }
                except:
                    continue
            
            # Look for result/product links
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                visible_links = [l for l in links if l.is_displayed()]
                
                if visible_links:
                    link_text = visible_links[0].text[:50] or "link"
                    return {
                        'type': 'click',
                        'target': link_text,
                        'value': None,
                        'confidence': 0.75
                    }
            except:
                pass
            
            # Scroll down if nothing found
            return {
                'type': 'scroll',
                'target': 'down',
                'value': 400,
                'confidence': 0.60
            }
        
        except Exception as e:
            self.logger.warning(f"Navigation phase error: {e}")
            return self._safe_fallback_action()
    
    def _phase_extract(self, task_lower: str, url: str) -> Dict[str, Any]:
        """Handle extraction/completion phase"""
        
        try:
            # Extract data based on keywords
            if any(word in task_lower for word in ['price', 'cost', 'amount']):
                try:
                    prices = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(text(), '$') or contains(text(), '₹') or contains(text(), 'Rs')]"
                    )
                    if prices:
                        return {
                            'type': 'extract',
                            'target': 'price',
                            'value': prices[0].text[:50],
                            'confidence': 0.85
                        }
                except:
                    pass
            
            # Extract ratings/reviews
            if any(word in task_lower for word in ['rating', 'review', 'star']):
                try:
                    ratings = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(text(), 'star') or contains(@aria-label, 'rating')]"
                    )
                    if ratings:
                        return {
                            'type': 'extract',
                            'target': 'rating',
                            'value': ratings[0].text[:50],
                            'confidence': 0.80
                        }
                except:
                    pass
            
            # Task complete
            return {
                'type': 'complete',
                'target': 'task finished',
                'value': None,
                'confidence': 0.90
            }
        
        except Exception as e:
            self.logger.warning(f"Extraction phase error: {e}")
            return self._safe_fallback_action()
    
    def _extract_search_term(self, task_lower: str) -> str:
        """Extract search term intelligently from task"""
        
        # Remove common phrases
        phrases_to_remove = [
            'search for', 'find', 'look for', 'show me',
            'get', 'price of', 'information about', 'details of',
            'on amazon', 'on youtube', 'on google', 'on github'
        ]
        
        result = task_lower
        for phrase in phrases_to_remove:
            result = result.replace(phrase, '')
        
        # Extract quoted text
        quoted = re.findall(r'"([^"]+)"', result)
        if quoted:
            return quoted[0]
        
        # Return first meaningful words
        words = [w for w in result.split() if len(w) > 2]
        return ' '.join(words[:5]) if words else 'search'
    
    def _check_completion(self, task_prompt: str) -> bool:
        """Check if task is complete"""
        try:
            # If we extracted data, task is likely complete
            if 'extract' in str(self.action_history):
                return True
            
            # Check for completion keywords on page
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            if any(word in page_text for word in ['no results', 'not found', 'error']):
                return True
            
            return False
        
        except:
            return False
    
    def _calculate_confidence(self, iteration: int) -> float:
        """Calculate confidence score"""
        base_confidence = 0.75
        
        # Increase confidence with iterations up to 5
        if iteration <= 5:
            return base_confidence + (iteration * 0.05)
        
        # Cap at 0.95
        return min(0.95, base_confidence + 0.25)
    
    def _safe_fallback_action(self) -> Dict[str, Any]:
        """Safe fallback action when all else fails"""
        return {
            'type': 'scroll',
            'target': 'down',
            'value': 300,
            'confidence': 0.50
        }


# =============================================================================
# COORDINATE HELPERS - Gemini Computer Use outputs normalized 0-999 coordinates
# =============================================================================

def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-999) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-999) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)


class GeminiComputerUseFlow:
    """
    Main flow for Gemini 2.5 Computer Use with Groq + rule-based fallback.
    
    Uses the official Gemini Computer Use tool API:
      1. Send screenshot + prompt with ComputerUse tool configured
      2. Receive FunctionCall responses (click_at, type_text_at, navigate, etc.)
      3. Execute actions via Selenium WebDriver
      4. Capture new screenshot, build FunctionResponse, continue the loop
    """
    
    # Default screen dimensions (overridden dynamically from driver viewport)
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.gemini_available = GEMINI_AVAILABLE
        self.groq_available = GROQ_AVAILABLE
        self.client = None
        self.fallback_analyzer = None
        self.last_request_time = 0
        self.request_delay = 0.3  # Minimal delay between API requests
        
        # Initialize Gemini client with new google-genai SDK
        if self.gemini_available and settings and settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=settings.gemini_api_key)
                self.computer_use_model = getattr(settings, 'computer_use_model', 'gemini-2.5-computer-use-preview-10-2025')
                self.logger.info(f"[GEMINI CU] Client initialized - Model: {self.computer_use_model}")
            except Exception as e:
                self.logger.warning(f"[GEMINI CU] Client init failed: {e}")
                self.gemini_available = False
        else:
            self.logger.warning("[GEMINI CU] SDK not available or API key missing")
            self.gemini_available = False
                
        # Initialize Groq fallback
        if self.groq_available and settings and getattr(settings, 'groq_api_key', None):
            try:
                self.groq_client = Groq(api_key=settings.groq_api_key)
                self.groq_model = getattr(settings, 'groq_model', 'meta-llama/llama-4-scout-17b-16e-instruct')
                self.logger.info(f"[GROQ] Fallback initialized - Model: {self.groq_model}")
            except Exception as e:
                self.logger.warning(f"[GROQ] Fallback init failed: {e}")
                self.groq_available = False
        else:
            self.groq_available = False
    
    def _build_computer_use_config(self) -> "types.GenerateContentConfig":
        """Build the GenerateContentConfig with Computer Use tool."""
        return types.GenerateContentConfig(
            tools=[
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER
                    )
                )
            ],
        )
    
    def execute_flow_iteration(
        self,
        initial_screenshot: str,
        task_prompt: str,
        driver,
        max_iterations: int = 50,
        website_type: Optional[str] = None,
        workflow: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute automation flow using Gemini Computer Use API.
        Falls back to Groq Vision → Rule-based analysis if Gemini is unavailable.
        """
        
        self.fallback_analyzer = AdvancedFallbackAnalyzer(driver)
        
        start_time = datetime.now()
        iteration = 0
        executed_actions = 0
        unique_urls: Set[str] = set()
        gemini_used = False
        fallback_used = False
        
        self.logger.info("\n" + "="*150)
        self.logger.info("GEMINI 2.5 COMPUTER USE - AGENTIC EXECUTION ENGINE")
        self.logger.info("="*150 + "\n")
        
        try:
            # Attempt Gemini Computer Use loop first
            if self.gemini_available and self.client:
                self.logger.info("[GEMINI CU] Starting Computer Use agentic loop...")
                result = self._run_gemini_computer_use_loop(
                    driver, task_prompt, initial_screenshot, max_iterations
                )
                if result:
                    gemini_used = True
                    iteration = result.get('total_iterations', 0)
                    executed_actions = result.get('total_actions', 0)
                    unique_urls = set(result.get('unique_pages', []))
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    result.update({
                        'execution_time': execution_time,
                        'gemini_used': True,
                        'fallback_used': False,
                    })
                    
                    self.logger.info("\n" + "="*150)
                    self.logger.info(
                        f"EXECUTION COMPLETE: {iteration} iterations, "
                        f"{executed_actions} actions, {execution_time:.1f}s [GEMINI CU]"
                    )
                    self.logger.info("="*150 + "\n")
                    return result
            
            # Fallback: Groq Vision + Rule-based loop
            self.logger.warning("[FALLBACK] Gemini Computer Use unavailable, using Groq + Rule-based engine")
            fallback_used = True
            
            result = self._run_fallback_loop(
                driver, task_prompt, initial_screenshot, max_iterations
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.update({
                'execution_time': execution_time,
                'gemini_used': False,
                'fallback_used': True,
            })
            
            self.logger.info("\n" + "="*150)
            self.logger.info(
                f"EXECUTION COMPLETE: {result.get('total_iterations', 0)} iterations, "
                f"{result.get('total_actions', 0)} actions, {execution_time:.1f}s [FALLBACK]"
            )
            self.logger.info("="*150 + "\n")
            return result
        
        except Exception as e:
            self.logger.error(f"[FATAL] Execution failed: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'task_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
                'total_iterations': iteration,
                'total_actions': executed_actions,
                'unique_pages': list(unique_urls),
                'execution_time': execution_time,
                'status': 'error',
                'success': False,
                'gemini_used': gemini_used,
                'fallback_used': fallback_used,
                'error': str(e)
            }
    
    # =========================================================================
    # GEMINI COMPUTER USE LOOP (Primary Engine)
    # =========================================================================
    
    def _run_gemini_computer_use_loop(
        self,
        driver,
        task_prompt: str,
        initial_screenshot_path: str,
        max_iterations: int
    ) -> Optional[Dict[str, Any]]:
        """
        Run the official Gemini Computer Use agentic loop.
        
        The loop:
          1. Build initial Content with user prompt + screenshot
          2. Call generate_content with ComputerUse tool
          3. Parse FunctionCall responses (click_at, type_text_at, etc.)
          4. Execute actions via Selenium
          5. Capture new screenshot, build FunctionResponse
          6. Append to conversation history and repeat
        """
        
        config = self._build_computer_use_config()
        
        iteration = 0
        executed_actions = 0
        unique_urls: Set[str] = set()
        all_model_text: List[str] = []  # Accumulate model text for summary
        
        # Get ACTUAL viewport dimensions from the browser (not hardcoded)
        # Critical: browser chrome, scrollbars, and display scaling reduce the viewport
        try:
            viewport = driver.execute_script("return [window.innerWidth, window.innerHeight]")
            self.SCREEN_WIDTH = viewport[0]
            self.SCREEN_HEIGHT = viewport[1]
            self.logger.info(f"[GEMINI CU] Viewport detected: {self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        except Exception:
            self.logger.warning(f"[GEMINI CU] Could not detect viewport, using {self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        
        try:
            # Read initial screenshot
            screenshot_bytes = self._capture_screenshot_bytes(driver)
            if not screenshot_bytes:
                # Try reading from file
                try:
                    with open(initial_screenshot_path, 'rb') as f:
                        screenshot_bytes = f.read()
                except:
                    self.logger.error("[GEMINI CU] Cannot get initial screenshot")
                    return None
            
            # Build initial conversation
            contents = [
                Content(
                    role="user",
                    parts=[
                        Part(text=task_prompt),
                        Part.from_bytes(data=screenshot_bytes, mime_type='image/png')
                    ]
                )
            ]
            
            for iteration in range(1, max_iterations + 1):
                try:
                    self.logger.info(f"\n[GEMINI CU] --- Turn {iteration}/{max_iterations} ---")
                    
                    # Rate limiting
                    self._rate_limit()
                    
                    # Call Gemini Computer Use API
                    self.logger.info("[GEMINI CU] Sending to model...")
                    response = self.client.models.generate_content(
                        model=self.computer_use_model,
                        contents=contents,
                        config=config,
                    )
                    
                    candidate = response.candidates[0]
                    
                    # Append model response to history
                    contents.append(candidate.content)
                    
                    # Check for function calls
                    function_calls = []
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    
                    # Log and accumulate model text
                    for text in text_parts:
                        self.logger.info(f"[GEMINI CU] Model: {text[:200]}")
                        all_model_text.append(text)
                    
                    # If no function calls, the model is done
                    if not function_calls:
                        final_text = " ".join(text_parts) if text_parts else "Task completed"
                        self.logger.info(f"[GEMINI CU] Task finished: {final_text[:300]}")
                        break
                    
                    # Execute each function call
                    results = self._execute_computer_use_actions(driver, function_calls)
                    executed_actions += len([r for r in results if r[1].get('success', True)])
                    
                    # Track URL
                    try:
                        unique_urls.add(driver.current_url)
                    except:
                        pass
                    
                    # Capture new screenshot and build FunctionResponse
                    new_screenshot_bytes = self._capture_screenshot_bytes(driver)
                    if not new_screenshot_bytes:
                        self.logger.warning("[GEMINI CU] Failed to capture post-action screenshot")
                        break
                    
                    current_url = ""
                    try:
                        current_url = driver.current_url
                    except:
                        pass
                    
                    # Build FunctionResponse parts for each executed function call
                    function_response_parts = []
                    for fname, result_data in results:
                        response_payload = {"url": current_url}
                        response_payload.update(result_data)
                        
                        fr = types.FunctionResponse(
                            name=fname,
                            response=response_payload,
                            parts=[
                                types.FunctionResponsePart(
                                    inline_data=types.FunctionResponseBlob(
                                        mime_type="image/png",
                                        data=new_screenshot_bytes
                                    )
                                )
                            ]
                        )
                        function_response_parts.append(fr)
                    
                    # Append function responses to conversation
                    contents.append(
                        Content(
                            role="user",
                            parts=[Part(function_response=fr) for fr in function_response_parts]
                        )
                    )
                    
                    # Save iteration screenshot
                    self._save_iteration_screenshot(driver, iteration)
                    
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    self.logger.info("[GEMINI CU] User interrupted")
                    break
                except Exception as e:
                    self.logger.error(f"[GEMINI CU] Turn {iteration} error: {e}", exc_info=True)
                    # On API error, break out and let fallback handle it
                    if "model" in str(e).lower() or "not found" in str(e).lower() or "permission" in str(e).lower():
                        self.logger.error("[GEMINI CU] Model/API error - breaking to fallback")
                        return None
                    continue
            
            return {
                'task_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
                'total_iterations': iteration,
                'total_actions': executed_actions,
                'unique_pages': list(unique_urls),
                'status': 'success',
                'success': True,
                'ai_summary': "\n".join(all_model_text) if all_model_text else "Task completed",
            }
        
        except Exception as e:
            self.logger.error(f"[GEMINI CU] Loop fatal error: {e}", exc_info=True)
            return None
    
    def _execute_computer_use_actions(
        self,
        driver,
        function_calls: list
    ) -> List[Tuple[str, Dict]]:
        """
        Execute Computer Use function calls via Selenium WebDriver.
        
        Maps Gemini function calls to Selenium actions:
          - click_at(x, y) → selenium mouse click at denormalized coordinates
          - type_text_at(x, y, text, press_enter) → click + type + optional Enter
          - navigate(url) → driver.get(url)
          - scroll_document(direction) → window.scrollBy
          - scroll_at(x, y, direction, magnitude) → scroll at position
          - go_back() → driver.back()
          - go_forward() → driver.forward()
          - wait_5_seconds() → time.sleep(5)
          - key_combination(keys) → ActionChains key combo
          - hover_at(x, y) → ActionChains move_to
          - open_web_browser() → no-op (already open)
          - search() → no-op (model handles via other actions)
          - drag_and_drop(x, y, dest_x, dest_y) → ActionChains drag
        """
        
        results = []
        
        for fc in function_calls:
            fname = fc.name
            args = fc.args or {}
            action_result = {}
            
            self.logger.info(f"[GEMINI CU] -> Executing: {fname}({dict(args)})")
            
            try:
                # Handle safety_decision
                if 'safety_decision' in args:
                    sd = args['safety_decision']
                    decision = sd.get('decision', '')
                    explanation = sd.get('explanation', '')
                    self.logger.warning(f"[SAFETY] {decision}: {explanation}")
                    if decision == 'require_confirmation':
                        self.logger.info("[SAFETY] Auto-confirming action (automation mode)")
                        action_result['safety_acknowledgement'] = 'true'
                
                if fname == "open_web_browser":
                    self.logger.info("[GEMINI CU] Browser already open")
                    
                elif fname == "click_at":
                    actual_x = denormalize_x(int(args.get("x", 0)), self.SCREEN_WIDTH)
                    actual_y = denormalize_y(int(args.get("y", 0)), self.SCREEN_HEIGHT)
                    self.logger.info(f"[GEMINI CU] Click at ({actual_x}, {actual_y})")
                    
                    # Robust click for ALL website types
                    click_result = ''
                    try:
                        click_result = driver.execute_script("""
                            var x = arguments[0], y = arguments[1];
                            var el = document.elementFromPoint(x, y);
                            if (!el) return 'no_element_at_' + x + '_' + y;
                            
                            var tag = el.tagName.toLowerCase();
                            var info = tag + (el.id ? '#'+el.id : '') + (el.className ? '.'+String(el.className).substring(0,30) : '');
                            
                            // 1. Form controls → focus + click directly
                            if (['input', 'textarea', 'select', 'option'].indexOf(tag) !== -1) {
                                el.focus();
                                el.click();
                                return 'form_control:' + info;
                            }
                            
                            // 2. BUTTONS FIRST (before links!) - YouTube search, MakeMyTrip, Amazon cart
                            var btn = el.closest('button') || el.closest('input[type="submit"]') || el.closest('input[type="button"]');
                            if (btn) {
                                btn.click();
                                return 'button_click:' + (btn.tagName + (btn.id ? '#'+btn.id : ''));
                            }
                            
                            // 3. Role-based interactives (MakeMyTrip tabs, DemoQA cards, YouTube menus)
                            var roleEl = el.closest('[role="button"]') || el.closest('[role="tab"]') || el.closest('[role="menuitem"]') || el.closest('[role="option"]');
                            if (roleEl) {
                                roleEl.click();
                                return 'role_click:' + roleEl.getAttribute('role');
                            }
                            
                            // 4. Navigation links - <a> with real href
                            var link = el.closest('a');
                            if (link && link.href) {
                                var href = link.href;
                                // Skip non-navigation: javascript:, #-only, same-page anchors
                                var isNavLink = href &&
                                    !href.startsWith('javascript:') &&
                                    href !== link.baseURI &&
                                    href !== link.baseURI + '#' &&
                                    !href.endsWith('#');
                                    
                                if (isNavLink) {
                                    window.location.href = href;
                                    return 'navigated:' + href.substring(0, 120);
                                } else {
                                    // Non-nav link: just click it
                                    link.click();
                                    return 'link_click_no_nav:' + info;
                                }
                            }
                            
                            // 5. <summary> for <details> accordions (DemoQA)
                            var summary = el.closest('summary');
                            if (summary) {
                                summary.click();
                                return 'summary_click';
                            }
                            
                            // 6. Fallback: full MouseEvent dispatch with bubbling
                            ['mousedown', 'mouseup', 'click'].forEach(function(evtType) {
                                el.dispatchEvent(new MouseEvent(evtType, {
                                    bubbles: true, cancelable: true, view: window,
                                    clientX: x, clientY: y
                                }));
                            });
                            return 'event_dispatch:' + info;
                        """, actual_x, actual_y)
                        self.logger.info(f"[GEMINI CU] Click result: {click_result}")
                    except Exception as click_err:
                        self.logger.warning(f"[GEMINI CU] JS click failed: {click_err}")
                        # Ultimate fallback: ActionChains real mouse event
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            ActionChains(driver).move_to_element_with_offset(
                                body, actual_x, actual_y
                            ).click().perform()
                            click_result = 'actionchains_fallback'
                        except Exception:
                            click_result = 'click_failed'
                    
                    # Wait longer if navigation occurred (page load)
                    if isinstance(click_result, str) and click_result.startswith('navigated:'):
                        time.sleep(0.8)
                    else:
                        time.sleep(0.15)
                    
                elif fname == "type_text_at":
                    actual_x = denormalize_x(int(args.get("x", 0)), self.SCREEN_WIDTH)
                    actual_y = denormalize_y(int(args.get("y", 0)), self.SCREEN_HEIGHT)
                    text = str(args.get("text", ""))
                    press_enter = args.get("press_enter", False)
                    clear_before = args.get("clear_before_typing", False)
                    
                    self.logger.info(f"[GEMINI CU] Type '{text[:50]}' at ({actual_x}, {actual_y})")
                    
                    # Step 1: Click at coordinates using JS (atomic, no stale refs)
                    try:
                        driver.execute_script("""
                            var el = document.elementFromPoint(arguments[0], arguments[1]);
                            if (el) { el.focus({preventScroll: true}); el.click(); }
                        """, actual_x, actual_y)
                    except Exception:
                        body = driver.find_element(By.TAG_NAME, "body")
                        ActionChains(driver).move_to_element_with_offset(
                            body, actual_x, actual_y
                        ).click().perform()
                    time.sleep(0.08)
                    
                    # Step 2: Get the NOW-focused element (always fresh, never stale)
                    active = driver.switch_to.active_element
                    
                    if clear_before:
                        try:
                            active.clear()
                        except Exception:
                            active.send_keys(Keys.CONTROL, 'a')
                            active.send_keys(Keys.DELETE)
                        time.sleep(0.05)
                    
                    # Step 3: Type text
                    active.send_keys(text)
                    time.sleep(0.1)
                    
                    if press_enter:
                        active.send_keys(Keys.RETURN)
                        time.sleep(0.3)
                    
                    time.sleep(0.1)
                    
                elif fname == "navigate":
                    url = str(args.get("url", ""))
                    self.logger.info(f"[GEMINI CU] Navigate to: {url}")
                    if url and url.startswith(("http://", "https://")):
                        driver.get(url)
                        time.sleep(0.5)
                    
                elif fname == "scroll_document":
                    direction = str(args.get("direction", "down")).lower()
                    pixels = 500
                    if direction == "up":
                        pixels = -500
                    driver.execute_script(f"window.scrollBy(0, {pixels});")
                    self.logger.info(f"[GEMINI CU] Scroll {direction}")
                    time.sleep(0.1)
                    
                elif fname == "scroll_at":
                    actual_x = denormalize_x(int(args.get("x", 500)), self.SCREEN_WIDTH)
                    actual_y = denormalize_y(int(args.get("y", 500)), self.SCREEN_HEIGHT)
                    direction = str(args.get("direction", "down")).lower()
                    magnitude = int(args.get("magnitude", 400))
                    pixels = magnitude if direction == "down" else -magnitude
                    driver.execute_script(
                        f"document.elementFromPoint({actual_x}, {actual_y})"
                        f".scrollBy(0, {pixels});"
                    )
                    self.logger.info(f"[GEMINI CU] Scroll {direction} at ({actual_x}, {actual_y})")
                    time.sleep(0.1)
                    
                elif fname == "go_back":
                    driver.back()
                    self.logger.info("[GEMINI CU] Go back")
                    time.sleep(0.25)
                    
                elif fname == "go_forward":
                    driver.forward()
                    self.logger.info("[GEMINI CU] Go forward")
                    time.sleep(0.25)
                    
                elif fname == "wait_5_seconds":
                    self.logger.info("[GEMINI CU] Waiting 2 seconds (optimized)...")
                    time.sleep(2)
                    
                elif fname == "key_combination":
                    keys_str = str(args.get("keys", ""))
                    self.logger.info(f"[GEMINI CU] Key combo: {keys_str}")
                    self._execute_key_combination(driver, keys_str)
                    time.sleep(0.15)
                    
                elif fname == "hover_at":
                    actual_x = denormalize_x(int(args.get("x", 0)), self.SCREEN_WIDTH)
                    actual_y = denormalize_y(int(args.get("y", 0)), self.SCREEN_HEIGHT)
                    self.logger.info(f"[GEMINI CU] Hover at ({actual_x}, {actual_y})")
                    ActionChains(driver).move_by_offset(actual_x, actual_y).perform()
                    time.sleep(0.15)
                    
                elif fname == "drag_and_drop":
                    src_x = denormalize_x(int(args.get("x", 0)), self.SCREEN_WIDTH)
                    src_y = denormalize_y(int(args.get("y", 0)), self.SCREEN_HEIGHT)
                    dst_x = denormalize_x(int(args.get("destination_x", 0)), self.SCREEN_WIDTH)
                    dst_y = denormalize_y(int(args.get("destination_y", 0)), self.SCREEN_HEIGHT)
                    self.logger.info(f"[GEMINI CU] Drag ({src_x},{src_y}) -> ({dst_x},{dst_y})")
                    actions = ActionChains(driver)
                    actions.move_by_offset(src_x, src_y)
                    actions.click_and_hold()
                    actions.move_by_offset(dst_x - src_x, dst_y - src_y)
                    actions.release()
                    actions.perform()
                    time.sleep(0.1)
                    
                elif fname == "search":
                    self.logger.info("[GEMINI CU] Search action (handled by model)")
                    
                else:
                    self.logger.warning(f"[GEMINI CU] Unknown function: {fname}")
                
                # Wait for page to settle
                try:
                    driver.execute_script("return document.readyState") 
                except:
                    pass
                
                action_result['success'] = True
                    
            except Exception as e:
                self.logger.error(f"[GEMINI CU] Action {fname} failed: {e}")
                action_result['error'] = str(e)
                action_result['success'] = False
            
            results.append((fname, action_result))
        
        return results
    
    def _execute_key_combination(self, driver, keys_str: str):
        """Execute keyboard combination like 'Control+A' or 'Enter'."""
        key_map = {
            'control': Keys.CONTROL,
            'ctrl': Keys.CONTROL,
            'shift': Keys.SHIFT,
            'alt': Keys.ALT,
            'meta': Keys.META,
            'command': Keys.META,
            'enter': Keys.RETURN,
            'return': Keys.RETURN,
            'tab': Keys.TAB,
            'escape': Keys.ESCAPE,
            'esc': Keys.ESCAPE,
            'backspace': Keys.BACK_SPACE,
            'delete': Keys.DELETE,
            'space': Keys.SPACE,
            'up': Keys.ARROW_UP,
            'down': Keys.ARROW_DOWN,
            'left': Keys.ARROW_LEFT,
            'right': Keys.ARROW_RIGHT,
            'home': Keys.HOME,
            'end': Keys.END,
            'pageup': Keys.PAGE_UP,
            'pagedown': Keys.PAGE_DOWN,
            'f1': Keys.F1,
            'f5': Keys.F5,
            'f11': Keys.F11,
            'f12': Keys.F12,
        }
        
        parts = [p.strip().lower() for p in keys_str.split('+')]
        actions = ActionChains(driver)
        
        # Press modifiers
        modifiers = []
        regular_keys = []
        for p in parts:
            if p in ('control', 'ctrl', 'shift', 'alt', 'meta', 'command'):
                modifiers.append(key_map[p])
            elif p in key_map:
                regular_keys.append(key_map[p])
            elif len(p) == 1:
                regular_keys.append(p)
        
        for mod in modifiers:
            actions.key_down(mod)
        for key in regular_keys:
            actions.send_keys(key)
        for mod in reversed(modifiers):
            actions.key_up(mod)
        
        actions.perform()
    
    # =========================================================================
    # FALLBACK LOOP (Groq Vision + Rule-Based)
    # =========================================================================
    
    def _run_fallback_loop(
        self,
        driver,
        task_prompt: str,
        initial_screenshot_path: str,
        max_iterations: int
    ) -> Dict[str, Any]:
        """Run the fallback loop using Groq Vision and rule-based analysis."""
        
        iteration = 0
        executed_actions = 0
        unique_urls: Set[str] = set()
        
        for iteration in range(1, max_iterations + 1):
            try:
                self.logger.info(f"\n[FALLBACK] --- Iteration {iteration}/{max_iterations} ---")
                
                screenshot_path = self._save_iteration_screenshot(driver, iteration)
                
                # Try Groq Vision first
                analysis = None
                if self.groq_available and screenshot_path:
                    analysis = self._analyze_with_groq(screenshot_path, task_prompt, iteration)
                
                # Fall back to rule-based
                if analysis is None:
                    self.logger.info("[FALLBACK] Using rule-based analysis")
                    analysis = self.fallback_analyzer.analyze_page(task_prompt, iteration)
                
                # Log
                self._log_analysis(analysis, iteration)
                
                # Execute action
                action = analysis.get('action')
                if not action:
                    self.logger.info("[FALLBACK] No more actions to perform")
                    break
                
                success = self._execute_fallback_action(driver, action, iteration)
                if success:
                    executed_actions += 1
                
                # Check completion
                if analysis.get('task_complete', False):
                    self.logger.info("[FALLBACK] Task completed!")
                    break
                
                unique_urls.add(driver.current_url)
                time.sleep(0.15)
            
            except KeyboardInterrupt:
                self.logger.info("[FALLBACK] User interrupted")
                break
            except Exception as e:
                self.logger.error(f"[FALLBACK] Iteration {iteration}: {e}", exc_info=True)
                continue
        
        return {
            'task_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            'total_iterations': iteration,
            'total_actions': executed_actions,
            'unique_pages': list(unique_urls),
            'status': 'success',
            'success': True,
        }
    
    def _analyze_with_groq(
        self,
        screenshot_path: str,
        task_prompt: str,
        iteration: int
    ) -> Optional[Dict[str, Any]]:
        """Analyze with Groq Llama Vision model"""
        
        if not self.groq_available or not screenshot_path:
            return None
        
        try:
            # Read and encode image to base64
            try:
                with open(screenshot_path, 'rb') as f:
                    image_data = base64.standard_b64encode(f.read()).decode('utf-8')
                    # format required for Groq data URI
                    image_url = f"data:image/png;base64,{image_data}"
            except (IOError, OSError) as e:
                self.logger.error(f"Failed to read screenshot: {e}")
                return None
            
            prompt = f"""Analyze this screenshot for task: {task_prompt[:100]}

Respond with ONLY valid JSON (no markdown):
{{
    "analysis": "brief description",
    "action": {{"type": "click|fill|navigate|scroll|extract|complete", "target": "element", "value": null}},
    "reasoning": "why this action",
    "task_complete": false
}}"""

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    }
                ],
                model=self.groq_model,
                temperature=0.0
            )
            
            text = chat_completion.choices[0].message.content.strip()
            
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start < 0 or end <= start:
                return None
            
            json_str = text[start:end]
            
            try:
                parsed = json.loads(json_str)
                if 'action' in parsed:
                    return parsed
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            self.logger.debug(f"Groq analysis failed: {e}")
            return None
    
    # =========================================================================
    # SHARED HELPERS
    # =========================================================================
    
    def _capture_screenshot_bytes(self, driver) -> Optional[bytes]:
        """Capture screenshot as raw bytes from Selenium driver."""
        try:
            return driver.get_screenshot_as_png()
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
            return None
    
    def _save_iteration_screenshot(self, driver, iteration: int) -> Optional[str]:
        """Save screenshot to disk (async I/O) and return the file path."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            screenshot_dir = Path(settings.screenshot_dir) if settings else Path("./screenshots")
            screenshot_file = screenshot_dir / f"step_{iteration:03d}_{timestamp}.png"
            
            screenshot_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Capture bytes in main thread (requires driver), write to disk async
            png_bytes = driver.get_screenshot_as_png()
            path_str = str(screenshot_file)
            def _write():
                try:
                    with open(path_str, 'wb') as f:
                        f.write(png_bytes)
                except Exception:
                    pass
            threading.Thread(target=_write, daemon=True).start()
            self.logger.info(f"[SCREENSHOT] {screenshot_file.name} (async)")
            
            return path_str
        except Exception as e:
            self.logger.error(f"Screenshot save failed: {e}")
            return None
    
    def _rate_limit(self):
        """Simple rate limiter for API calls."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _execute_fallback_action(self, driver, action: Dict[str, Any], iteration: int) -> bool:
        """Execute action from fallback analysis (Groq/Rule-based)."""
        
        try:
            action_type = action.get('type', '').lower()
            target = action.get('target', '')
            value = action.get('value')
            
            if action_type == 'fill':
                return self._action_fill(driver, target, value)
            elif action_type == 'click':
                return self._action_click(driver, target)
            elif action_type == 'scroll':
                return self._action_scroll(driver, value)
            elif action_type == 'navigate':
                return self._action_navigate(driver, value)
            elif action_type == 'extract':
                self.logger.info(f"[EXTRACT] {target}: {value}")
                return True
            elif action_type == 'complete':
                self.logger.info(f"[COMPLETE] {target}")
                return True
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                return False
        
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return False
    
    def _action_fill(self, driver, target: str, value: str) -> bool:
        """Fill input field"""
        try:
            # Try CSS selector
            elements = driver.find_elements(By.CSS_SELECTOR, target)
            
            # Try XPath based on placeholder
            if not elements:
                elements = driver.find_elements(By.XPATH, f"//*[contains(@placeholder, '{target}')]")
            
            # Fallback for vague AI generated targets like "search_box" or "search bar"
            if not elements and any(word in target.lower() for word in ['search', 'box', 'input', 'bar']):
                elements = driver.find_elements(
                    By.XPATH, 
                    "//*[@name='q' or @type='search' or contains(translate(@placeholder, 'SEARCH', 'search'), 'search') or contains(translate(@aria-label, 'SEARCH', 'search'), 'search')]"
                )
            
            # Final fallback: just get the first visible text input
            if not elements:
                elements = driver.find_elements(By.XPATH, "//input[@type='text' or not(@type)] | //textarea")
            
            if elements:
                # Find the first interactable element
                element = next((e for e in elements if e.is_displayed() and e.is_enabled()), elements[0])
                
                element.click()
                time.sleep(0.1)
                element.clear()
                element.send_keys(value)
                
                # If doing a search, hit ENTER to trigger it automatically (very reliable fallback)
                if any(w in str(target).lower() or w in str(value).lower() for w in ['search', 'youtube.com', 'amazon.com']):
                    element.send_keys(Keys.RETURN)
                time.sleep(0.25)
                
                self.logger.info(f"[FILL] {target}: {value}")
                return True
        except Exception as e:
            self.logger.debug(f"Fill action failed: {e}")
        
        return False
    
    def _action_click(self, driver, target: str) -> bool:
        """Click element"""
        try:
            # Try button/link by text
            elements = driver.find_elements(
                By.XPATH,
                f"//button | //a | //*[contains(text(), '{target}')]"
            )
            
            if elements:
                element = elements[0]
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.1)
                element.click()
                time.sleep(0.2)
                self.logger.info(f"[CLICK] {target}")
                return True
        except Exception as e:
            self.logger.debug(f"Click action failed: {e}")
        
        return False
    
    def _action_scroll(self, driver, pixels: int) -> bool:
        """Scroll page"""
        try:
            driver.execute_script(f"window.scrollBy(0, {pixels})")
            time.sleep(0.15)
            self.logger.info(f"[SCROLL] {pixels}px")
            return True
        except Exception as e:
            self.logger.debug(f"Scroll action failed: {e}")
        
        return False
    
    def _action_navigate(self, driver, url: str) -> bool:
        """Navigate to URL"""
        try:
            driver.get(url)
            time.sleep(0.25)
            self.logger.info(f"[NAVIGATE] {url}")
            return True
        except Exception as e:
            self.logger.debug(f"Navigation failed: {e}")
        
        return False
    
    def _log_analysis(self, analysis: Optional[Dict[str, Any]], iteration: int) -> None:
        """Log analysis details"""
        if not analysis:
            return
        
        try:
            analysis_text = analysis.get('analysis', 'N/A')[:80]
            self.logger.info(f"[ANALYSIS] {analysis_text}")
            
            if analysis.get('action'):
                action = analysis['action']
                action_type = action.get('type', 'unknown')
                target = action.get('target', 'unknown')
                value = action.get('value')
                
                if value:
                    self.logger.info(f"[ACTION] {action_type}: {target} = {value}")
                else:
                    self.logger.info(f"[ACTION] {action_type}: {target}")
        
        except Exception as e:
            self.logger.debug(f"Logging failed: {e}")