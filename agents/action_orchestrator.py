"""
Action Orchestrator - Complete with Real Form Filling and Smooth Automation
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException, NoSuchElementException
)
import traceback

from config.settings import settings
from logging_config.logger import get_logger

logger = get_logger(__name__)


class ActionOrchestrator:
    """Orchestrate automation with REAL interactions"""

    def __init__(self, driver, action_executor):
        self.driver = driver
        self.executor = action_executor
        self.logger = get_logger(self.__class__.__name__)
        self.visited_urls = set()
        self.intelligence_data = {
            'selectors': [],
            'forms': [],
            'interactions': [],
            'filled_fields': [],
            'page_structure': {}
        }
        self.wait = WebDriverWait(driver, 10)

    def execute_plan(self, execution_plan: Dict) -> Dict[str, Any]:
        """Execute the plan"""
        start_time = datetime.now()
        results = {
            'task_id': execution_plan.get('task_id'),
            'status': 'running',
            'executed_actions': [],
            'errors': [],
            'visited_pages': [],
            'intelligence': self.intelligence_data,
            'reasoning': [],
            'start_time': start_time.isoformat()
        }

        try:
            sub_tasks = execution_plan.get('sub_tasks', [])

            for task in sub_tasks:
                try:
                    action = task.get('action')
                    description = task.get('description')
                    
                    self.logger.info(f"[ACTION] {description}")
                    result = self._execute_action(action, task)

                    results['executed_actions'].append({
                        'action': action,
                        'description': description,
                        'status': 'success' if result else 'failed',
                        'timestamp': datetime.now().isoformat()
                    })

                except Exception as e:
                    self.logger.error(f"Task error: {str(e)}")
                    results['errors'].append(str(e))

        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))

        finally:
            results['status'] = 'completed'
            results['visited_pages'] = list(self.visited_urls)
            results['end_time'] = datetime.now().isoformat()
            execution_time = (datetime.now() - start_time).total_seconds()
            results['execution_time'] = round(execution_time, 2)
            results['reasoning'] = self._generate_reasoning(results)

        return results

    def _execute_action(self, action: str, task: Dict) -> bool:
        """Execute single action"""
        try:
            if action == 'screenshot':
                return self._take_screenshot(task)
            elif action == 'extract_data':
                return self._extract_page_data()
            elif action == 'explore_all_pages':
                return self._explore_all_pages_with_interaction()
            elif action == 'interact_forms':
                return self._interact_with_all_forms()
            elif action == 'extract_comprehensive_data':
                return self._extract_comprehensive_data()
            elif action == 'generate_report':
                return self._generate_report()
            else:
                self.logger.warning(f"Unknown action: {action}")
                return False
        except Exception as e:
            self.logger.error(f"Action error ({action}): {str(e)}")
            return False

    def _take_screenshot(self, task: Dict) -> bool:
        """Take screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = settings.screenshot_path / filename
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"[OK] Screenshot saved")
            return True
        except Exception as e:
            self.logger.error(f"Screenshot error: {str(e)}")
            return False

    def _extract_page_data(self) -> bool:
        """Extract page data"""
        try:
            title = self.driver.title
            url = self.driver.current_url
            self.logger.info(f"[OK] Analyzed: {title}")
            return True
        except Exception as e:
            self.logger.error(f"Data extraction error: {str(e)}")
            return False

    def _explore_all_pages_with_interaction(self) -> bool:
        """Explore ALL pages AND interact with forms"""
        try:
            self.logger.info("[EXPLORE] Starting comprehensive exploration with interactions...")
            
            base_url = self.driver.current_url
            self.visited_urls.add(base_url)
            
            pages_explored = 0
            max_pages = 50
            
            while pages_explored < max_pages:
                current_url = self.driver.current_url
                self.logger.info(f"[PAGE {pages_explored+1}] {current_url}")
                
                # INTERACT WITH FORMS ON CURRENT PAGE
                self._fill_all_forms_on_page()
                
                # INTERACT WITH BUTTONS
                self._click_interactive_buttons()
                
                # Take screenshot
                self._take_screenshot({})
                
                # Extract data
                self._extract_page_data()
                
                # Get links to next pages
                try:
                    links = self._get_all_clickable_links()
                    self.logger.info(f"[LINKS] Found {len(links)} navigation links")
                    
                    if not links:
                        break
                    
                    # Navigate to first unvisited link
                    navigated = False
                    for link_info in links:
                        url = link_info.get('href')
                        text = link_info.get('text')
                        
                        if not url or url in self.visited_urls:
                            continue
                        
                        if not self._is_same_domain(url):
                            continue
                        
                        try:
                            self.logger.info(f"[NAVIGATE] {text}")
                            self.driver.get(url)
                            time.sleep(2)
                            
                            self.visited_urls.add(url)
                            pages_explored += 1
                            navigated = True
                            break
                            
                        except Exception as e:
                            self.logger.warning(f"Navigation error: {str(e)}")
                            continue
                    
                    if not navigated:
                        break
                    
                except Exception as e:
                    self.logger.warning(f"Link extraction error: {str(e)}")
                    break
            
            self.logger.info(f"[COMPLETE] Explored {pages_explored} pages with interactions")
            return pages_explored > 0
            
        except Exception as e:
            self.logger.error(f"Exploration error: {str(e)}")
            traceback.print_exc()
            return False

    def _fill_all_forms_on_page(self) -> bool:
        """ACTUALLY FILL ALL FORMS ON CURRENT PAGE"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            if not forms:
                return False
            
            self.logger.info(f"[FORMS] Found {len(forms)} forms on this page")
            
            for form_idx, form in enumerate(forms):
                try:
                    self.logger.info(f"[FILL] Filling form {form_idx + 1}/{len(forms)}")
                    self._fill_single_form(form)
                except Exception as e:
                    self.logger.warning(f"Form fill error: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Form detection error: {str(e)}")
            return False

    def _fill_single_form(self, form) -> bool:
        """Fill a single form with test data"""
        try:
            # Get all input fields
            inputs = form.find_elements(By.TAG_NAME, 'input')
            textareas = form.find_elements(By.TAG_NAME, 'textarea')
            selects = form.find_elements(By.TAG_NAME, 'select')
            
            # Test data mapping
            test_data = {
                'firstName': 'John',
                'lastName': 'Automation',
                'email': 'test@automation.com',
                'mobile': '9876543210',
                'name': 'Test User',
                'subject': 'Testing Automation',
                'message': 'This is automated testing message',
                'username': 'testuser123',
                'password': 'TestPass123!',
                'confirm': 'TestPass123!',
                'currentAddress': '123 Test Street, Test City',
                'permanentAddress': '456 Test Avenue, Test State',
                'fullName': 'Test Automation User',
                'phone': '9876543210'
            }
            
            # Fill text inputs
            for inp in inputs:
                try:
                    input_type = inp.get_attribute('type')
                    name = inp.get_attribute('name')
                    placeholder = inp.get_attribute('placeholder')
                    
                    # Skip buttons and hidden fields
                    if input_type in ['submit', 'button', 'hidden', 'file']:
                        continue
                    
                    # Handle checkboxes and radio buttons
                    if input_type in ['checkbox', 'radio']:
                        if not inp.is_selected():
                            try:
                                inp.click()
                                self.logger.info(f"[CLICK] {input_type}: {name}")
                                time.sleep(0.5)
                            except:
                                pass
                        continue
                    
                    # Get appropriate test value
                    value = test_data.get(name) or test_data.get(placeholder) or f"test_{name}"
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                    time.sleep(0.3)
                    
                    # Click and fill
                    inp.click()
                    time.sleep(0.2)
                    inp.clear()
                    time.sleep(0.1)
                    
                    # Type with realistic delay
                    for char in value:
                        inp.send_keys(char)
                        time.sleep(0.05)
                    
                    self.logger.info(f"[FILL] {name}: {value[:20]}...")
                    time.sleep(0.3)
                    
                    # Track field
                    self.intelligence_data['filled_fields'].append({
                        'name': name,
                        'type': input_type,
                        'value': value
                    })
                    
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.warning(f"Input fill error: {str(e)}")
                    continue
            
            # Fill textareas
            for textarea in textareas:
                try:
                    textarea.click()
                    time.sleep(0.2)
                    textarea.clear()
                    textarea.send_keys("Automated testing content for validation")
                    self.logger.info(f"[FILL] textarea")
                    time.sleep(0.3)
                except Exception as e:
                    self.logger.warning(f"Textarea error: {str(e)}")
                    continue
            
            # Handle selects
            for select in selects:
                try:
                    sel = Select(select)
                    options = sel.options
                    
                    if len(options) > 1:
                        sel.select_by_index(1)
                        self.logger.info(f"[SELECT] dropdown option")
                        time.sleep(0.3)
                except Exception as e:
                    self.logger.warning(f"Select error: {str(e)}")
                    continue
            
            # Try to submit form if submit button exists
            try:
                submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                self.logger.info(f"[SUBMIT] Form submitted")
                time.sleep(1)
            except:
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Form fill error: {str(e)}")
            return False

    def _click_interactive_buttons(self) -> bool:
        """Click interactive buttons (alerts, modals, etc)"""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            
            for idx, button in enumerate(buttons[:5]):
                try:
                    if button.is_displayed():
                        text = button.text[:30]
                        
                        # Scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.2)
                        
                        # Click
                        button.click()
                        self.logger.info(f"[CLICK] Button: {text}")
                        time.sleep(0.5)
                        
                        # Handle alerts if any
                        try:
                            alert = self.wait.until(EC.alert_is_present())
                            alert.accept()
                            self.logger.info(f"[ALERT] Accepted alert")
                            time.sleep(0.5)
                        except:
                            pass
                
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.warning(f"Button click error: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Button interaction error: {str(e)}")
            return False

    def _get_all_clickable_links(self) -> List[Dict]:
        """Get all navigation links"""
        try:
            links = []
            anchor_elements = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for anchor in anchor_elements:
                try:
                    href = anchor.get_attribute('href')
                    text = anchor.text.strip()
                    
                    if href and text and not href.startswith('javascript'):
                        if not any(l['href'] == href for l in links):
                            links.append({'href': href, 'text': text})
                            
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
            
            return links[:50]
            
        except Exception as e:
            self.logger.error(f"Link retrieval error: {str(e)}")
            return []

    def _is_same_domain(self, url: str) -> bool:
        """Check if same domain"""
        try:
            if url.startswith('/'):
                return True
            current = self.driver.current_url.split('/')[2]
            new = url.split('/')[2]
            return current == new
        except:
            return url.startswith('/')

    def _interact_with_all_forms(self) -> bool:
        """Interact with forms - compatibility method"""
        return self._fill_all_forms_on_page()

    def _extract_comprehensive_data(self) -> bool:
        """Extract all intelligence data"""
        try:
            self.logger.info("[INTELLIGENCE] Extracting complete data...")
            
            selectors = self._extract_selectors()
            forms = self._extract_forms_data()
            interactions = self._extract_interactions()
            
            self.intelligence_data['selectors'].extend(selectors)
            self.intelligence_data['forms'].extend(forms)
            self.intelligence_data['interactions'].extend(interactions)
            
            self.logger.info(f"[DATA] Selectors: {len(selectors)} | Forms: {len(forms)} | Interactions: {len(interactions)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Data extraction error: {str(e)}")
            return False

    def _extract_selectors(self) -> List[Dict]:
        """Extract CSS selectors"""
        selectors = []
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, '[id], [class], input, button, a')
            for elem in elements[:50]:
                try:
                    selectors.append({
                        'tag': elem.tag_name,
                        'id': elem.get_attribute('id'),
                        'class': elem.get_attribute('class'),
                        'name': elem.get_attribute('name')
                    })
                except:
                    pass
        except:
            pass
        return selectors

    def _extract_forms_data(self) -> List[Dict]:
        """Extract form data"""
        forms = []
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, 'form')
            for form in form_elements:
                try:
                    form_data = {
                        'id': form.get_attribute('id'),
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method'),
                        'fields': len(form.find_elements(By.TAG_NAME, 'input'))
                    }
                    forms.append(form_data)
                except:
                    pass
        except:
            pass
        return forms

    def _extract_interactions(self) -> List[Dict]:
        """Extract interactive elements"""
        interactions = []
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons[:20]:
                try:
                    interactions.append({
                        'type': 'button',
                        'text': btn.text[:30],
                        'id': btn.get_attribute('id')
                    })
                except:
                    pass
        except:
            pass
        return interactions

    def _generate_report(self) -> bool:
        """Generate report"""
        try:
            report = {
                'title': 'Automation Intelligence Report',
                'timestamp': datetime.now().isoformat(),
                'total_pages_explored': len(self.visited_urls),
                'pages_visited': list(self.visited_urls),
                'total_fields_filled': len(self.intelligence_data['filled_fields']),
                'intelligence': self.intelligence_data
            }
            
            report_file = settings.screenshot_path / 'intelligence_report.json'
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"[REPORT] Saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Report error: {str(e)}")
            return False

    def _generate_reasoning(self, results: Dict) -> List[str]:
        """Generate AI reasoning"""
        reasoning = []
        
        reasoning.append(f"[ANALYSIS]")
        reasoning.append(f"  - Pages explored: {len(self.visited_urls)}")
        reasoning.append(f"  - Forms filled: {len([f for f in self.intelligence_data['filled_fields']])}")
        reasoning.append(f"  - Fields filled: {len(self.intelligence_data['filled_fields'])}")
        reasoning.append(f"  - Execution time: {results.get('execution_time', 0)}s")
        reasoning.append(f"  - Errors: {len(results['errors'])}")
        
        reasoning.append(f"\n[PAGES VISITED]")
        for page in list(self.visited_urls)[:8]:
            reasoning.append(f"  - {page}")
        if len(self.visited_urls) > 8:
            reasoning.append(f"  - ... and {len(self.visited_urls) - 8} more")
        
        reasoning.append(f"\n[STATUS]")
        if results['errors']:
            reasoning.append(f"  Completed with {len(results['errors'])} warnings")
        else:
            reasoning.append(f"  [OK] Completed successfully")
        
        return reasoning