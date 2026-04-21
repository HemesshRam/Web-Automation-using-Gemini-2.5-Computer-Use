"""
Scraping Workflow
Workflow for data scraping
"""

from typing import Dict, List, Any
from datetime import datetime
from selenium.webdriver.common.by import By

from .base_workflow import BaseWorkflow
from handlers.element_handler import ElementHandler


class ScrapingWorkflow(BaseWorkflow):
    """Workflow for data scraping operations"""
    
    def __init__(self, driver, selectors: Dict[str, str]):
        """Initialize scraping workflow"""
        super().__init__("ScrapingWorkflow")
        self.driver = driver
        self.selectors = selectors
        self.element_handler = ElementHandler(driver)
        self.scraped_data = []
    
    def execute(self) -> Dict[str, Any]:
        """Execute scraping workflow"""
        self.start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting scraping workflow with {len(self.selectors)} selectors")
            
            for name, selector in self.selectors.items():
                self.scrape_element(name, selector)
            
            self.log_result("SUCCESS", f"Scraped {len(self.scraped_data)} items")
            
        except Exception as e:
            self.logger.error(f"Scraping workflow failed: {str(e)}")
            self.log_result("FAILED", f"Scraping failed: {str(e)}")
        
        finally:
            self.end_time = datetime.now()
        
        return self.get_results()
    
    def scrape_element(self, name: str, selector: str):
        """Scrape single element"""
        try:
            text = self.element_handler.get_element_text(selector)
            if text:
                self.scraped_data.append({'name': name, 'value': text})
                self.logger.info(f"Scraped: {name} = {text[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Failed to scrape {name}: {str(e)}")