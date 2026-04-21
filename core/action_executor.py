"""
Action Executor - SPEED OPTIMIZED
Executes individual automation actions on web elements.
Optimizations applied:
  1. JS-accelerated input filling  – replaces char-by-char loop with a single
     native-value-setter call; dispatches input/change events for React/Vue.
  2. Smart DOM-stable wait          – polls readyState+jQuery instead of sleeping.
  3. 3-attempt click cascade        – direct → ActionChains → JS force-click;
     no wasted retries when the first attempt succeeds.
  4. Single scrollIntoView call     – {block:'center'} reduces layout repaints.
  5. Batched scroll in FAST_MODE    – one JS call instead of N round-trips.
  6. Configurable FAST_MODE flag    – flip to False to restore human-like timing.
  7. Minimal fixed delays           – replaced 1-5 s random sleeps with 50 ms.
"""

import time
from typing import Any, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)

from config.settings import settings
from logging_config.logger import get_logger
from detectors.anti_bot_service import AntiBotService
from handlers.element_handler import ElementHandler

logger = get_logger(__name__)

# ── Speed profile ─────────────────────────────────────────────────────────────
# FAST_MODE = True  → minimal delays, JS-accelerated typing (recommended)
# FAST_MODE = False → human-like timing (restores original behaviour)
FAST_MODE: bool = True

_PRE_CLICK_DELAY  = 0.05   # was: random 1–5 s
_POST_CLICK_DELAY = 0.05   # was: random 1–5 s
_SCROLL_SETTLE    = 0.10   # was: 0.3 s
_FOCUS_SETTLE     = 0.05   # was: 0.1 s
_CLEAR_SETTLE     = 0.05   # was: 0.1 s
_SCROLL_STEP      = 0.10   # was: random 1–5 s per scroll step
_KEYS_SETTLE      = 0.05   # was: random 1–5 s
# ──────────────────────────────────────────────────────────────────────────────


def _pre_delay(svc: "AntiBotService") -> None:
    time.sleep(_PRE_CLICK_DELAY if FAST_MODE else svc.get_random_delay())


def _post_delay(svc: "AntiBotService") -> None:
    time.sleep(_POST_CLICK_DELAY if FAST_MODE else svc.get_random_delay())


def _wait_for_dom_stable(driver, timeout: float = 2.0) -> None:
    """Poll document.readyState + jQuery.active instead of sleeping blindly."""
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
        time.sleep(0.05)
    time.sleep(0.10)   # graceful fallback if page never idles


class ActionExecutor:
    """Execute individual automation actions – speed-optimised."""

    def __init__(self, driver, anti_bot_service: Optional[AntiBotService] = None):
        self.driver = driver
        self.anti_bot_service = anti_bot_service or AntiBotService()
        self.element_handler = ElementHandler(driver)
        self.wait = WebDriverWait(driver, settings.element_wait_timeout)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _scroll_to(self, element) -> None:
        """Scroll element to viewport centre in a single JS call."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center',inline:'nearest'});",
            element,
        )
        time.sleep(_SCROLL_SETTLE if FAST_MODE else 0.3)

    def _js_fill(self, element, value: str) -> None:
        """
        Instant JS fill – sets native input value and fires React/Vue events.
        Falls back to send_keys if the native setter is unavailable.
        """
        try:
            self.driver.execute_script(
                """
                var el  = arguments[0];
                var val = arguments[1];
                var proto = el.tagName === 'TEXTAREA'
                    ? window.HTMLTextAreaElement.prototype
                    : window.HTMLInputElement.prototype;
                var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(el, val);
                el.dispatchEvent(new Event('input',  {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                """,
                element,
                value,
            )
        except Exception:
            element.clear()
            element.send_keys(value)

    # ── Public API ─────────────────────────────────────────────────────────────

    def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Click element: direct → ActionChains → JS force-click cascade.
        Anti-bot delays kept minimal in FAST_MODE.
        """
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, selector)))
            _pre_delay(self.anti_bot_service)
            self._scroll_to(element)

            # Attempt 1 – direct click (fastest; best for event propagation)
            try:
                element.click()
                _post_delay(self.anti_bot_service)
                logger.info(f"Clicked element: {selector}")
                return True
            except ElementNotInteractableException:
                pass

            # Attempt 2 – ActionChains (bypasses some overlay issues)
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                _post_delay(self.anti_bot_service)
                logger.info(f"Clicked (ActionChains): {selector}")
                return True
            except Exception:
                pass

            # Attempt 3 – JS force-click (ignores overlays / stale state)
            self.driver.execute_script("arguments[0].click();", element)
            _post_delay(self.anti_bot_service)
            logger.info(f"Clicked (JS force): {selector}")
            return True

        except TimeoutException:
            logger.warning(f"Element not clickable within timeout: {selector}")
            return False
        except Exception as exc:
            logger.error(f"Failed to click element {selector}: {exc}")
            return False

    def fill_input(
        self,
        selector: str,
        value: str,
        by: By = By.CSS_SELECTOR,
        clear_first: bool = True,
    ) -> bool:
        """
        Fill input field.
        FAST_MODE  : JS native-value setter – instant single DOM write.
        Normal mode: char-by-char send_keys with realistic typing delays.
        """
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            self._scroll_to(element)

            # Focus
            try:
                element.click()
            except Exception:
                self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(_FOCUS_SETTLE if FAST_MODE else 0.1)

            # Clear
            if clear_first:
                try:
                    element.clear()
                except Exception:
                    self.driver.execute_script("arguments[0].value = '';", element)
                time.sleep(_CLEAR_SETTLE if FAST_MODE else 0.1)

            if FAST_MODE:
                self._js_fill(element, value)
            else:
                for char in value:
                    element.send_keys(char)
                    time.sleep(self.anti_bot_service.get_realistic_typing_delay())

            logger.info(f"Filled input field: {selector}")
            return True

        except TimeoutException:
            logger.warning(f"Input field not found within timeout: {selector}")
            return False
        except Exception as exc:
            logger.error(f"Failed to fill input {selector}: {exc}")
            return False

    def select_dropdown(
        self, selector: str, value: str, by: By = By.CSS_SELECTOR
    ) -> bool:
        """Select dropdown option: try by value, then by visible text."""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            select = Select(element)

            try:
                select.select_by_value(value)
                _post_delay(self.anti_bot_service)
                logger.info(f"Selected dropdown option (value): {value}")
                return True
            except Exception:
                pass

            select.select_by_visible_text(value)
            _post_delay(self.anti_bot_service)
            logger.info(f"Selected dropdown option (text): {value}")
            return True

        except Exception as exc:
            logger.error(f"Failed to select dropdown {selector}: {exc}")
            return False

    def drag_and_drop(
        self,
        source_selector: str,
        target_selector: str,
        by: By = By.CSS_SELECTOR,
    ) -> bool:
        """Perform drag and drop action."""
        try:
            source = self.wait.until(
                EC.presence_of_element_located((by, source_selector))
            )
            target = self.wait.until(
                EC.presence_of_element_located((by, target_selector))
            )
            _pre_delay(self.anti_bot_service)
            ActionChains(self.driver).drag_and_drop(source, target).perform()
            _post_delay(self.anti_bot_service)
            logger.info(f"Drag and drop: {source_selector} → {target_selector}")
            return True
        except Exception as exc:
            logger.error(f"Drag and drop failed: {exc}")
            return False

    def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """
        Scroll page.
        FAST_MODE: single JS call for all steps (eliminates N round-trips).
        Normal:    per-step with randomised anti-bot delay.
        """
        try:
            px_per_step = 300
            sign = -1 if direction.lower() == "up" else 1
            total_px = px_per_step * amount * sign

            if FAST_MODE:
                self.driver.execute_script(f"window.scrollBy(0, {total_px});")
                time.sleep(_SCROLL_STEP)
            else:
                for _ in range(amount):
                    self.driver.execute_script(
                        f"window.scrollBy(0, {px_per_step * sign});"
                    )
                    time.sleep(self.anti_bot_service.get_random_delay())

            logger.info(f"Scrolled {direction} by {amount} steps")
            return True
        except Exception as exc:
            logger.error(f"Scroll failed: {exc}")
            return False

    def send_keys(self, selector: str, keys: str, by: By = By.CSS_SELECTOR) -> bool:
        """Send keyboard keys to element."""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by, selector))
            )
            element.send_keys(keys)
            time.sleep(
                _KEYS_SETTLE if FAST_MODE else self.anti_bot_service.get_random_delay()
            )
            logger.info(f"Sent keys to element: {selector}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send keys: {exc}")
            return False

    def execute_javascript(self, script: str) -> Any:
        """Execute arbitrary JavaScript code."""
        try:
            result = self.driver.execute_script(script)
            logger.info("JavaScript executed successfully")
            return result
        except Exception as exc:
            logger.error(f"JavaScript execution failed: {exc}")
            return None

    def wait_for_element(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: Optional[int] = None,
    ) -> bool:
        """Wait for element to be present in the DOM."""
        try:
            t = timeout or settings.element_wait_timeout
            WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"Element found: {selector}")
            return True
        except TimeoutException:
            logger.warning(f"Element not found within {timeout}s: {selector}")
            return False

    def wait_for_dom_stable(self, timeout: float = 2.0) -> None:
        """Block until DOM is stable (network idle + readyState complete)."""
        _wait_for_dom_stable(self.driver, timeout)