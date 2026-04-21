"""
Website Workflow Handler
Executes predefined workflows for specific websites
Handles: Amazon, YouTube, Yahoo Finance, MakeMyTrip, GitHub, Booking, Flipkart, Alibaba
"""

import time
from typing import Optional, Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from logging_config.logger import get_logger
from handlers.action_handler import ActionHandler
from handlers.element_handler import ElementHandler

logger = get_logger(__name__)


class AmazonWorkflow:
    """Amazon-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_product(self, product_name: str) -> Dict[str, Any]:
        """Search for product on Amazon"""
        try:
            logger.info(f"[AMAZON] Searching for: {product_name}")
            
            # Click search box
            if not self.action_handler.fill_input("input[name='field-keywords']", product_name):
                return {'success': False, 'error': 'Failed to fill search box'}
            
            # Click search button
            if not self.action_handler.click_element("input[value='Go']"):
                return {'success': False, 'error': 'Failed to click search button'}
            
            time.sleep(3)
            
            # Extract top result
            product_info = self._extract_product_info()
            
            return {
                'success': True,
                'product': product_info
            }
        
        except Exception as e:
            logger.error(f"[AMAZON] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_product_info(self) -> Dict[str, str]:
        """Extract product information from search results"""
        try:
            title = self.element_handler.get_element_text('h2 a span')
            price = self.element_handler.get_element_text('.a-price-whole')
            rating = self.element_handler.get_element_text('.a-icon-star-small span')
            
            return {
                'title': title or 'N/A',
                'price': price or 'N/A',
                'rating': rating or 'N/A'
            }
        
        except Exception as e:
            logger.error(f"[AMAZON] Product extraction failed: {str(e)}")
            return {}


class YouTubeWorkflow:
    """YouTube-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_videos(self, query: str) -> Dict[str, Any]:
        """Search for videos on YouTube"""
        try:
            logger.info(f"[YOUTUBE] Searching for: {query}")
            
            # Click search box
            if not self.action_handler.fill_input("#search input", query):
                return {'success': False, 'error': 'Failed to fill search box'}
            
            # Press Enter to search
            if not self.action_handler.press_key(Keys.RETURN):
                return {'success': False, 'error': 'Failed to press Enter'}
            
            time.sleep(4)
            
            # Extract top videos
            videos = self._extract_videos()
            
            return {
                'success': True,
                'videos': videos
            }
        
        except Exception as e:
            logger.error(f"[YOUTUBE] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_videos(self) -> List[Dict[str, str]]:
        """Extract video information"""
        try:
            videos = []
            elements = self.element_handler.find_elements('ytd-video-renderer')
            
            for element in elements[:5]:  # Top 5
                try:
                    title = element.find_element(By.CSS_SELECTOR, 'h3 a #video-title').get_attribute('title')
                    videos.append({'title': title})
                except:
                    pass
            
            return videos
        
        except Exception as e:
            logger.error(f"[YOUTUBE] Video extraction failed: {str(e)}")
            return []


class YahooFinanceWorkflow:
    """Yahoo Finance-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_stock(self, symbol: str) -> Dict[str, Any]:
        """Search for stock price"""
        try:
            logger.info(f"[YAHOO FINANCE] Searching for: {symbol}")
            
            # Click search box
            if not self.action_handler.fill_input("input[placeholder*='Symbol']", symbol):
                return {'success': False, 'error': 'Failed to fill search box'}
            
            # Press Enter
            if not self.action_handler.press_key(Keys.RETURN):
                return {'success': False, 'error': 'Failed to press Enter'}
            
            time.sleep(3)
            
            # Extract stock information
            stock_info = self._extract_stock_info()
            
            return {
                'success': True,
                'stock': stock_info
            }
        
        except Exception as e:
            logger.error(f"[YAHOO FINANCE] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_stock_info(self) -> Dict[str, str]:
        """Extract stock information"""
        try:
            current_price = self.element_handler.get_element_text('[data-test="qsp-current-price"]')
            
            return {
                'current_price': current_price or 'N/A'
            }
        
        except Exception as e:
            logger.error(f"[YAHOO FINANCE] Stock extraction failed: {str(e)}")
            return {}


class MakeMyTripWorkflow:
    """MakeMyTrip-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_flights(self, from_city: str, to_city: str) -> Dict[str, Any]:
        """Search for flights"""
        try:
            logger.info(f"[MAKEMYTRIP] Searching flights: {from_city} -> {to_city}")
            
            # Fill from city
            if not self.action_handler.fill_input("input[placeholder*='From']", from_city):
                return {'success': False, 'error': 'Failed to fill from city'}
            
            time.sleep(1)
            
            # Fill to city
            if not self.action_handler.fill_input("input[placeholder*='To']", to_city):
                return {'success': False, 'error': 'Failed to fill to city'}
            
            time.sleep(1)
            
            # Click search button
            if not self.action_handler.click_element("button[type='submit']"):
                return {'success': False, 'error': 'Failed to click search button'}
            
            time.sleep(5)
            
            # Extract flights
            flights = self._extract_flights()
            
            return {
                'success': True,
                'flights': flights
            }
        
        except Exception as e:
            logger.error(f"[MAKEMYTRIP] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_flights(self) -> List[Dict[str, str]]:
        """Extract flight information"""
        try:
            flights = []
            elements = self.element_handler.find_elements('div.flightCardContainer')
            
            for element in elements[:5]:  # Top 5
                try:
                    airline = element.find_element(By.CSS_SELECTOR, '.airline-name').text
                    price = element.find_element(By.CSS_SELECTOR, '.priceValue').text
                    flights.append({
                        'airline': airline,
                        'price': price
                    })
                except:
                    pass
            
            return flights
        
        except Exception as e:
            logger.error(f"[MAKEMYTRIP] Flight extraction failed: {str(e)}")
            return []


class GitHubWorkflow:
    """GitHub-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_repositories(self, query: str) -> Dict[str, Any]:
        """Search for repositories"""
        try:
            logger.info(f"[GITHUB] Searching for: {query}")
            
            # Click search box
            if not self.action_handler.fill_input("input[placeholder*='Search']", query):
                return {'success': False, 'error': 'Failed to fill search box'}
            
            # Press Enter
            if not self.action_handler.press_key(Keys.RETURN):
                return {'success': False, 'error': 'Failed to press Enter'}
            
            time.sleep(3)
            
            # Extract repositories
            repos = self._extract_repositories()
            
            return {
                'success': True,
                'repositories': repos
            }
        
        except Exception as e:
            logger.error(f"[GITHUB] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_repositories(self) -> List[Dict[str, str]]:
        """Extract repository information"""
        try:
            repos = []
            elements = self.element_handler.find_elements('div.Box-row')
            
            for element in elements[:5]:  # Top 5
                try:
                    name = element.find_element(By.CSS_SELECTOR, 'a[data-testid="repository-name"]').text
                    repos.append({'name': name})
                except:
                    pass
            
            return repos
        
        except Exception as e:
            logger.error(f"[GITHUB] Repository extraction failed: {str(e)}")
            return []


class BookingWorkflow:
    """Booking.com-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_hotels(self, destination: str) -> Dict[str, Any]:
        """Search for hotels"""
        try:
            logger.info(f"[BOOKING] Searching hotels in: {destination}")
            
            # Click destination field
            if not self.action_handler.fill_input("input[name='ss']", destination):
                return {'success': False, 'error': 'Failed to fill destination'}
            
            time.sleep(1)
            
            # Click search button
            if not self.action_handler.click_element("button[type='submit']"):
                return {'success': False, 'error': 'Failed to click search button'}
            
            time.sleep(5)
            
            # Extract hotels
            hotels = self._extract_hotels()
            
            return {
                'success': True,
                'hotels': hotels
            }
        
        except Exception as e:
            logger.error(f"[BOOKING] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_hotels(self) -> List[Dict[str, str]]:
        """Extract hotel information"""
        try:
            hotels = []
            elements = self.element_handler.find_elements('div[data-testid="property-card"]')
            
            for element in elements[:5]:  # Top 5
                try:
                    name = element.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text
                    hotels.append({'name': name})
                except:
                    pass
            
            return hotels
        
        except Exception as e:
            logger.error(f"[BOOKING] Hotel extraction failed: {str(e)}")
            return []


class FlipkartWorkflow:
    """Flipkart-specific automation workflow"""
    
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = ActionHandler(driver)
        self.element_handler = ElementHandler(driver)
    
    def search_products(self, product_name: str) -> Dict[str, Any]:
        """Search for products on Flipkart"""
        try:
            logger.info(f"[FLIPKART] Searching for: {product_name}")
            
            # Click search box
            if not self.action_handler.fill_input("input[placeholder*='Search']", product_name):
                return {'success': False, 'error': 'Failed to fill search box'}
            
            # Press Enter
            if not self.action_handler.press_key(Keys.RETURN):
                return {'success': False, 'error': 'Failed to press Enter'}
            
            time.sleep(3)
            
            # Extract products
            products = self._extract_products()
            
            return {
                'success': True,
                'products': products
            }
        
        except Exception as e:
            logger.error(f"[FLIPKART] Search failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_products(self) -> List[Dict[str, str]]:
        """Extract product information"""
        try:
            products = []
            elements = self.element_handler.find_elements('div._1AtVbE')
            
            for element in elements[:5]:  # Top 5
                try:
                    title = element.find_element(By.CSS_SELECTOR, 'a._2UzuGl').text
                    price = element.find_element(By.CSS_SELECTOR, '._30jeq3').text
                    products.append({
                        'title': title,
                        'price': price
                    })
                except:
                    pass
            
            return products
        
        except Exception as e:
            logger.error(f"[FLIPKART] Product extraction failed: {str(e)}")
            return []


class WorkflowFactory:
    """Factory for creating website-specific workflows"""
    
    WORKFLOWS = {
        'amazon': AmazonWorkflow,
        'youtube': YouTubeWorkflow,
        'yahoo_finance': YahooFinanceWorkflow,
        'makemytrip': MakeMyTripWorkflow,
        'github': GitHubWorkflow,
        'booking': BookingWorkflow,
        'flipkart': FlipkartWorkflow,
    }
    
    @staticmethod
    def create_workflow(website_type: str, driver):
        """Create workflow for website type"""
        workflow_class = WorkflowFactory.WORKFLOWS.get(website_type.lower())
        
        if workflow_class:
            logger.info(f"[WORKFLOW] Created for: {website_type}")
            return workflow_class(driver)
        
        logger.warning(f"[WORKFLOW] No specific workflow for: {website_type}")
        return None