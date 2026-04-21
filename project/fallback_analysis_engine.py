"""
Enhanced Fallback Analysis Engine - PRODUCTION READY
Rule-based intelligence for web automation
"""

import re
from typing import Dict, Any, Optional, List

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from logging_config.logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)


class FallbackAnalysisEngine:
    """Advanced rule-based analysis"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.visited_selectors = set()
    
    def analyze_page_intelligent(
        self,
        page_html: str,
        task_prompt: str,
        current_url: str,
        iteration: int,
        workflow_type: str,
        workflow_stage: str
    ) -> Dict[str, Any]:
        """Intelligent analysis using rules"""
        
        if not BS4_AVAILABLE:
            return self._safe_fallback_action()
        
        try:
            soup = BeautifulSoup(page_html, 'html.parser')
            
            if workflow_type == 'amazon_search':
                return self._analyze_amazon(soup, task_prompt, workflow_stage)
            elif workflow_type == 'yahoo_finance':
                return self._analyze_yahoo(soup, task_prompt, workflow_stage)
            elif workflow_type == 'youtube_search':
                return self._analyze_youtube(soup, task_prompt, workflow_stage)
            elif workflow_type == 'demoqa_exploration':
                return self._analyze_demoqa(soup, task_prompt, workflow_stage)
            else:
                return self._analyze_generic(soup, task_prompt, workflow_stage)
        
        except Exception as error:
            self.logger.error(f"[FALLBACK] Analysis error: {error}")
            return self._safe_fallback_action()
    
    def _analyze_amazon(self, soup, task_prompt: str, workflow_stage: str) -> Dict[str, Any]:
        """Amazon workflow"""
        
        if workflow_stage == 'navigate':
            return {
                'analysis': 'Navigating to Amazon',
                'action_type': 'navigate',
                'target': 'https://amazon.com',
                'value': None,
                'reasoning': 'Start at Amazon homepage',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'search':
            search_term = self._extract_search_term(task_prompt.lower())
            return {
                'analysis': 'Ready to search',
                'action_type': 'click',
                'target': 'input#twotabsearchtextbox',
                'value': search_term,
                'reasoning': f'Search for {search_term}',
                'stage_complete': False,
                'task_complete': False
            }
        
        elif workflow_stage == 'extract':
            return {
                'analysis': 'Extract products',
                'action_type': 'extract',
                'target': 'products',
                'value': None,
                'reasoning': 'Get product data',
                'stage_complete': True,
                'task_complete': True
            }
        
        return self._safe_fallback_action()
    
    def _analyze_yahoo(self, soup, task_prompt: str, workflow_stage: str) -> Dict[str, Any]:
        """Yahoo Finance workflow"""
        
        if workflow_stage == 'navigate':
            return {
                'analysis': 'Navigating to Yahoo Finance',
                'action_type': 'navigate',
                'target': 'https://finance.yahoo.com',
                'value': None,
                'reasoning': 'Start at Yahoo Finance',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'search':
            stock_symbol = self._extract_stock_symbol(task_prompt.lower())
            return {
                'analysis': 'Ready to search stock',
                'action_type': 'click',
                'target': 'input[placeholder*="Search"]',
                'value': stock_symbol,
                'reasoning': f'Search for {stock_symbol}',
                'stage_complete': False,
                'task_complete': False
            }
        
        elif workflow_stage == 'extract':
            return {
                'analysis': 'Extract stock data',
                'action_type': 'extract',
                'target': 'stock_data',
                'value': None,
                'reasoning': 'Get price info',
                'stage_complete': True,
                'task_complete': True
            }
        
        return self._safe_fallback_action()
    
    def _analyze_youtube(self, soup, task_prompt: str, workflow_stage: str) -> Dict[str, Any]:
        """YouTube workflow - FIXED"""
        
        if workflow_stage == 'navigate':
            return {
                'analysis': 'Navigating to YouTube',
                'action_type': 'navigate',
                'target': 'https://www.youtube.com',
                'value': None,
                'reasoning': 'Start at YouTube homepage',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'search':
            search_term = self._extract_search_term(task_prompt.lower())
            return {
                'analysis': 'Wait for search to be clickable',
                'action_type': 'wait',
                'target': 'input#search',
                'value': None,
                'reasoning': 'Wait for YouTube search input to load',
                'stage_complete': False,
                'task_complete': False
            }
        
        elif workflow_stage == 'navigate_result':
            search_term = self._extract_search_term(task_prompt.lower())
            return {
                'analysis': 'Searching YouTube',
                'action_type': 'fill',
                'target': 'input#search',
                'value': search_term,
                'reasoning': f'Type search term: {search_term}',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'extract':
            return {
                'analysis': 'Extract video info',
                'action_type': 'extract',
                'target': 'video_data',
                'value': None,
                'reasoning': 'Get video title and description',
                'stage_complete': True,
                'task_complete': True
            }
        
        return self._safe_fallback_action()
    
    def _analyze_demoqa(self, soup, task_prompt: str, workflow_stage: str) -> Dict[str, Any]:
        """DemoQA workflow"""
        
        if workflow_stage == 'navigate':
            return {
                'analysis': 'Navigating to DemoQA',
                'action_type': 'navigate',
                'target': 'https://demoqa.com',
                'value': None,
                'reasoning': 'Start at DemoQA',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'explore_module':
            return {
                'analysis': 'Exploring modules',
                'action_type': 'click',
                'target': 'div.card',
                'value': None,
                'reasoning': 'Click first module',
                'stage_complete': False,
                'task_complete': False
            }
        
        elif workflow_stage == 'extract':
            return {
                'analysis': 'Extract module data',
                'action_type': 'extract',
                'target': 'module_data',
                'value': None,
                'reasoning': 'Get module information',
                'stage_complete': True,
                'task_complete': True
            }
        
        return self._safe_fallback_action()
    
    def _analyze_generic(self, soup, task_prompt: str, workflow_stage: str) -> Dict[str, Any]:
        """Generic workflow"""
        
        if workflow_stage == 'navigate':
            return {
                'analysis': 'Stabilizing page',
                'action_type': 'scroll',
                'target': 'down',
                'value': 2,
                'reasoning': 'Load page content',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'action':
            search_term = self._extract_search_term(task_prompt.lower())
            return {
                'analysis': 'Looking for input',
                'action_type': 'fill',
                'target': 'input[type="text"]',
                'value': search_term,
                'reasoning': f'Enter: {search_term}',
                'stage_complete': True,
                'task_complete': False
            }
        
        elif workflow_stage == 'extract':
            return {
                'analysis': 'Extract page data',
                'action_type': 'extract',
                'target': 'page_data',
                'value': None,
                'reasoning': 'Get page info',
                'stage_complete': True,
                'task_complete': True
            }
        
        return self._safe_fallback_action()
    
    def _extract_search_term(self, task_lower: str) -> str:
        """Extract search term from task"""
        keywords = ['search', 'find', 'look', 'get', 'check']
        
        for keyword in keywords:
            if keyword in task_lower:
                idx = task_lower.find(keyword) + len(keyword)
                remaining = task_lower[idx:].strip()
                words = remaining.split()[:3]
                return ' '.join(words) if words else 'search'
        
        return 'search'
    
    def _extract_stock_symbol(self, task_lower: str) -> str:
        """Extract stock symbol"""
        symbols = ['tesla', 'apple', 'microsoft', 'google', 'amazon', 'nvidia']
        
        for symbol in symbols:
            if symbol in task_lower:
                return symbol.upper()
        
        return 'AAPL'
    
    def _safe_fallback_action(self) -> Dict[str, Any]:
        """Safe fallback action"""
        return {
            'analysis': 'Fallback action',
            'action_type': 'scroll',
            'target': 'down',
            'value': 2,
            'reasoning': 'Continue exploring',
            'stage_complete': False,
            'task_complete': False
        }