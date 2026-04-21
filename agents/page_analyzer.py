"""Page Analyzer Agent - Fixed Version"""

import json
import logging
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from config.settings import settings
from logging_config.logger import get_logger

logger = get_logger(__name__)


class PageAnalyzer:
    """Analyze page content and extract elements"""

    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

    def analyze_page(self) -> Dict[str, Any]:
        try:
            analysis = {
                'url': self.driver.current_url,
                'title': self._get_page_title(),
                'elements_found': self._extract_all_elements(),
                'forms_found': self._extract_forms(),
                'links_found': self._extract_links(),
                'buttons_found': self._extract_buttons(),
                'inputs_found': self._extract_inputs(),
                'page_state': 'ready'
            }

            self.logger.info(f"Page analysis: {analysis['url']}")
            return analysis

        except Exception as e:
            self.logger.error(f"Page analysis failed: {str(e)}")
            return {'error': str(e), 'page_state': 'error'}

    def _get_page_title(self) -> str:
        try:
            return self.driver.title
        except:
            return "Unknown"

    def _extract_all_elements(self) -> List[Dict]:
        elements = []
        try:
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, '*[id], *[class]')
            for elem in all_elements[:50]:
                try:
                    elements.append({
                        'tag': elem.tag_name,
                        'id': elem.get_attribute('id'),
                        'class': elem.get_attribute('class'),
                        'text': elem.text[:100] if elem.text else None
                    })
                except:
                    pass
        except:
            pass
        return elements

    def _extract_forms(self) -> List[Dict]:
        forms = []
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, 'form')
            for form in form_elements:
                try:
                    forms.append({
                        'id': form.get_attribute('id'),
                        'name': form.get_attribute('name'),
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method')
                    })
                except:
                    pass
        except:
            pass
        return forms

    def _extract_links(self) -> List[Dict]:
        links = []
        try:
            link_elements = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in link_elements[:30]:
                try:
                    href = link.get_attribute('href')
                    if href and not href.startswith('javascript'):
                        links.append({
                            'text': link.text[:50],
                            'href': href,
                            'visible': link.is_displayed()
                        })
                except:
                    pass
        except:
            pass
        return links

    def _extract_buttons(self) -> List[Dict]:
        buttons = []
        try:
            button_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            for button in button_elements[:20]:
                try:
                    buttons.append({
                        'text': button.text[:50],
                        'id': button.get_attribute('id'),
                        'class': button.get_attribute('class'),
                        'type': button.get_attribute('type')
                    })
                except:
                    pass
        except:
            pass
        return buttons

    def _extract_inputs(self) -> List[Dict]:
        inputs = []
        try:
            input_elements = self.driver.find_elements(By.TAG_NAME, 'input')
            for inp in input_elements[:30]:
                try:
                    inputs.append({
                        'name': inp.get_attribute('name'),
                        'type': inp.get_attribute('type'),
                        'id': inp.get_attribute('id'),
                        'placeholder': inp.get_attribute('placeholder'),
                        'required': inp.get_attribute('required') is not None
                    })
                except:
                    pass
        except:
            pass
        return inputs